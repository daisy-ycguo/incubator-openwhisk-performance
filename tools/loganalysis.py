#!/usr/bin/env python
# encoding: utf-8
'''
loganalysis -- analysis tool for openwhisk

loganalysis is a tool to extract performance data from log files.

It defines classes_and_methods

@author:     daisy-ycguo

@copyright:  2017 IBM. All rights reserved.

@license:    Apache 2.0

@contact:    guoyingc@cn.ibm.com
'''

import sys
import os
import string

from optparse import OptionParser

__all__ = []
__version__ = 0.1
__date__ = '2017-10-22'
__updated__ = '2017-10-22'


#log analysis main logic
docker_run_tag = 'invoker_docker.run_finish' # time to create a container by docker run
activation_init_tag = 'invoker_activationInit_finish' #time to initialize the action container, get the action ready
activation_run_tag = 'invoker_activationRun_finish' #time to run the action
docker_unpause_tag = 'invoker_docker.unpause_finish' #time for a warm start up by docker unpause
blocking_activation = 'controller_blockingActivation_finish' #time for an invocation in total
action_invocation_tag = 'POST /api/v1/namespaces/_/actions/'
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
        self.no_startup = 0
        self.execution_count = 0
        self.init_count = 0
        self.total_invocation_time = 0
        self.total_execution_time = 0
        self.total_warm_startup_time = 0
        self.total_cold_startup_time = 0
        self.total_init_time = 0
        self.max_invocation_time = 0
        self.min_invocation_time = 0
        self.max_execution_time = 0
        self.min_execution_time = 0
        self.max_warm_startup_time = 0
        self.min_warm_startup_time = 0
        self.max_cold_startup_time = 0
        self.min_cold_startup_time = 0
        self.max_init_time = 0
        self.min_init_time = 0
    
class transaction:
    def __init__(self):
        self.trans_num = '0000000000'
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
        return None,None
    end=line_str.find(']',start)
    trans_id=line_str[start-1:end+1]
    #get trans_number for example 0000059060
    start=trans_id.find('_')
    end=trans_id.find(']')
    number=trans_id[start+1:end]
    return trans_id,number.rjust(10,'0')

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

def log_analysis(filename_controller,filenames_invoker,outputfile):
    print 'into log_analysis'
    print 'controller log:'+filename_controller
    print 'invoker logs:'+filenames_invoker
    print 'output file:'+outputfile
    
    file_controller = open(filename_controller,"r")
    line = file_controller.readline()             
    while line:
        if line.find(action_invocation_tag)!=-1:
            trans = transaction()
            trans.trans_id,trans.trans_num = get_trans_id(line)
            #print trans.trans_id
            trans.action_name = get_action_name(line)
            #get data from invoker log
            invokers = filenames_invoker.split(',')
            for invoker_file_name in invokers:
                if get_info_from_invokerlog(invoker_file_name, trans):
                    break
            #print trans.activation_run
            trans_dict[trans.trans_num]=trans           
        line = file_controller.readline()
    file_controller.close()

    #get data from controller log
    file_controller = open(filename_controller,"r")
    line = file_controller.readline()             
    while line:
        if line.find(blocking_activation)!=-1:
            trans_id,trans_num = get_trans_id(line)
            activation_time = get_finish_time(line, 0)
            if trans_dict[trans_num]:
                trans_dict[trans_num].activation=activation_time
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

def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    #program_usage = '''usage: spam two eggs''' # optional - will be autogenerated by optparse
    program_longdesc = '''''' # optional - give further explanation about what the program does
    program_license = "Copyright 2017 daisy-ycguo (IBM)                                            \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-c", "--controllerlog", dest="contr_logfile", help="set controller log file", metavar="FILE")
        parser.add_option("-i", "--invokerlog", dest="invk_logfile", help="set invoker log files as a comma separated string, for example: invoker0.log,invoker1.log,invoker2.log ", metavar="FILE")
        parser.add_option("-o", "--outfile", dest="outfile", help="set output path [default: %default]", metavar="FILE")
        parser.add_option("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %default]")
        parser.add_option("-a", "--max", dest="max", action="count", help="set verbosity level [default: %default]")

        # set defaults
        parser.set_defaults(outfile="./out.txt")

        # process options
        (opts, args) = parser.parse_args(argv)

        if opts.verbose > 0:
            print("verbosity level = %d" % opts.verbose)
        if not opts.contr_logfile:
            print("required option controllerlog")
            return 2
        if not opts.invk_logfile:
            print("required option invokerlog")
            return 2
        if opts.outfile:
            print("outfile = %s" % opts.outfile)

        # MAIN BODY #
        log_analysis(opts.contr_logfile,opts.invk_logfile,opts.outfile)

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    code = main()
    if code != 0:
        sys.argv.append("-h")
        main()
    sys.exit(code)