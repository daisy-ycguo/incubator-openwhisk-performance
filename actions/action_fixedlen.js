
function main(param) {
    var timeout = param.timeout || '1';
    var interval = param.interval || '10';
    
    console.log("timeout="+timeout);
    console.log("interval="+interval);
    /*var timeoutobj = setTimeout(function() {
        clearInterval(intervalobj);
        console.log("time out");
        return {};
    }, 60000*parseInt(timeout));*/

    var intervalobj = setInterval(function() {
        console.log("I'm busy.");
    }, 10*parseInt(interval));

}

