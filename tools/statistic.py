'''
Created on Oct 20, 2017

@author: Daisy
'''
import string

docker_run_tag = 'invoker_docker.run_finish' # time to create a container by docker run
activation_init_tag = 'invoker_activationInit_finish' #time to initialize the action container, get the action ready
activation_run_tag = 'invoker_activationRun_finish' #time to run the action
docker_unpause_tag = 'invoker_docker.unpause_finish' #time for a warm start up by docker unpause
blocking_activation = 'controller_blockingActivation_finish' #time for an invocation in total

action_invocation_tag = 'POST /api/v1/namespaces/_/actions/'


filename_controller = "controller-0.log"
filenames_invoker = ("invoker0.log","invoker1.log","invoker2.log")
outputfile = "output.txt"
trans_dict = {}
actions_dict = {}

def analysis_data(trans_dict, actions_dict):
    for obj in trans_dict.values():
        if actions_dict.has_key(obj.action_name):
            action_record = actions_dict.get(obj.action_name)
            action_record.invocation_count+=1
            action_record.total_invocation_time+=obj.activation
            action_record.total_execution_time+=obj.activation_run
            action_record.total_warm_startup_time+=obj.activation_docker_unpause
            action_record.total_cold_startup_time+=obj.activation_docker_run
            action_record.total_init_time+=obj.activation_init
            if obj.activation==0:
                action_record.fail+=1
            else:
                action_record.success+=1
            if obj.activation_docker_run>0:
                action_record.cold_startup+=1
                if obj.activation==0:
                    print 'activation=0 but cold start up>0'+obj.trans_id
            if obj.activation_docker_unpause>0:
                action_record.warm_startup+=1
                if obj.activation==0:
                    print 'activation=0 but warm start up>0'+obj.trans_id
            if obj.activation>0 and obj.activation_docker_run==0 and obj.activation_docker_unpause==0:
                action_record.no_startup+=1
            if obj.activation_run>0:
                action_record.execution_count+=1
                if obj.activation==0:
                    print 'activation=0 but execution time>0'+obj.trans_id
            if obj.activation_init>0:
                action_record.init_count+=1
                if obj.activation==0:
                    print 'activation=0 but execution time>0'+obj.trans_id
        else:
            print "new dict"
            action_record = action_statisitic()
            action_record.action_name = obj.action_name
            actions_dict[action_record.action_name]=action_record    

    
def write_actions_dict_tofile(ooutput_file,action_record):
    ooutput_file.write('------'+action_record.action_name+"-------\r\n")
    ooutput_file.write('total invocations: '+str(action_record.invocation_count)+", including\r\n")
    ooutput_file.write("\t fail invocations: "+str(action_record.fail)+"\r\n")
    ooutput_file.write("\t success invocations: "+str(action_record.success)+", including \r\n")
    ooutput_file.write("\t\t cold startup: "+str(action_record.cold_startup)+"\r\n")
    ooutput_file.write("\t\t warm startup: "+str(action_record.warm_startup)+"\r\n")
    ooutput_file.write("\t\t no startup: "+str(action_record.no_startup)+"\r\n")
    ooutput_file.write("\t total init count: "+str(action_record.init_count)+"\r\n")
    ooutput_file.write("\t total execution count: "+str(action_record.execution_count)+"\r\n")
    
    ooutput_file.write('average innovation time is: '+str(action_record.total_invocation_time/action_record.success)+" .\r\n")
    ooutput_file.write('average execution time is: '+str(action_record.total_execution_time/action_record.execution_count)+" .\r\n")
    ooutput_file.write('average cold start up time is: '+str(action_record.total_cold_startup_time/action_record.cold_startup)+" .\r\n")
    ooutput_file.write('average warm start up time is: '+str(action_record.total_warm_startup_time/action_record.warm_startup)+" .\r\n")
    ooutput_file.write('average init time is: '+str(action_record.total_init_time/action_record.init_count)+" .\r\n")
    
def write_to_file(output_file_obj,trans):
    output_file_obj.write('action name:'+trans.action_name+'\r\n')
    output_file_obj.write('\t transaction id:'+trans.trans_id+'\r\n')
    output_file_obj.write('\t activation time:'+str(trans.activation)+'ms \r\n')
    output_file_obj.write('\t activation init time:'+str(trans.activation_init)+'ms \r\n')
    output_file_obj.write('\t action execute time:'+str(trans.activation_run)+'ms \r\n')
    output_file_obj.write('\t activation cold start up time:'+str(trans.activation_docker_run)+'ms \r\n')
    output_file_obj.write('\t activation warm start up time:'+str(trans.activation_docker_unpause)+'ms \r\n')
    
class action_statisitic:
    def __init__(self):
        self.action_name = ''
        self.invocation_count = 0
        self.fail = 0
        self.success = 0
        self.warm_startup = 0
        self.cold_startup = 0
        self.total_invocation_time = 0
        self.total_execution_time = 0
        self.total_warm_startup_time = 0
        self.total_cold_startup_time = 0
        self.total_init_time = 0
        self.no_startup = 0
        self.execution_count = 0
        self.init_count = 0
    
class transaction:
    def __init__(self):
        self.trans_id = ''
        self.action_name = ''
        self.activation = 0
        self.activation_init = 0
        self.activation_run = 0
        self.activation_docker_run = 0
        self.activation_docker_unpause = 0
        
# return: [#tid_59060]
def get_trans_id(line_str):
    start=line_str.find('#tid')
    if start==-1:
        return None
    end=line_str.find(']',start)
    return line_str[start-1:end+1]

def get_action_name(line_str):
    start=line_str.find('actions/')
    if (start==-1):
        return None
    end=line_str.find(' ',start)
    return line_str[start+8:end]

def get_finish_time(line_str,start):
    st = line_str.find('_finish',start)
    st = line_str.find(':',st+8)
    end = line_str.find(']',st)
    return string.atoi(line_str[st+1:end])
    
def get_info_from_invokerlog(logfile, trans):
    found = False
    file_invoker = open(logfile,"r")
    line = file_invoker.readline()
    while line:
        if line.find(trans.trans_id) !=-1 and line.find('marker:invoker')!=-1:
            found = True
            if line.find(docker_run_tag)!=-1:
                trans.activation_docker_run = get_finish_time(line,0)
            if line.find(activation_init_tag)!=-1:
                trans.activation_init = get_finish_time(line,0)
            if line.find(activation_run_tag)!=-1:
                trans.activation_run = get_finish_time(line,0)
            if line.find(docker_unpause_tag)!=-1:
                trans.activation_docker_unpause = get_finish_time(line,0)
            #if trans.activation_docker_unpause>0 or trans.activation_docker_run>0:
                #print trans.trans_id
        line = file_invoker.readline()
    file_invoker.close()
    return found

if __name__ == '__main__':
    file_controller = open(filename_controller,"r")
    line = file_controller.readline()             
    while line:
        if line.find(action_invocation_tag)!=-1:
            trans = transaction()
            trans.trans_id = get_trans_id(line)
            #print trans.trans_id
            trans.action_name = get_action_name(line)
            #get data from invoker log
            for invoker_file_name in filenames_invoker:
                if get_info_from_invokerlog(invoker_file_name, trans):
                    break
            #print trans.activation_run
            trans_dict[trans.trans_id]=trans           
        line = file_controller.readline()
    file_controller.close()

    #get data from controller log
    file_controller = open(filename_controller,"r")
    line = file_controller.readline()             
    while line:
        if line.find(blocking_activation)!=-1:
            trans_id = get_trans_id(line)
            activation_time = get_finish_time(line, 0)
            if trans_dict[trans_id]:
                trans_dict[trans_id].activation=activation_time
                #print activation_time
        line = file_controller.readline()
    file_controller.close()
    
    #analysis data
    analysis_data(trans_dict, actions_dict)
    
    #create output file
    outputobj = open(outputfile,"w")
    
    #write analysis data to output file
    for obj in actions_dict.values():
        write_actions_dict_tofile(outputobj, obj)
    outputobj.write('\r\n--------------------\r\n')
    
    #write original data to output file
    for obj in sorted(trans_dict.keys()):
        write_to_file(outputobj, trans_dict.get(obj))
    outputobj.flush()
    outputobj.close()
