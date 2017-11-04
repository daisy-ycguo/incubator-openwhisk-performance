
function main(param) {
    var timeout = param.timeout || '1';
    var interval = param.interval || '10';
    
    console.log("timeout="+timeout);
    console.log("interval="+interval);

    var promise = new Promise(function(resolve, reject) {
        var timeoutobj = setTimeout(function() {
            clearInterval(intervalobj);
            console.log("time out");
            resolve({message: 'time out!'});
        }, 60000*parseInt(timeout));

        var intervalobj = setInterval(function() {
            console.log("I'm busy.");
        }, 100*parseInt(interval));
    });

    return promise;

}

