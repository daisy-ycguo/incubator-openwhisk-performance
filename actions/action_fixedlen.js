
function main(param) {
    var timeout = param.timeout || '1';
    var interval = param.interval || '10';

    var timeoutobj = setTimeout(function() {
        clearInterval(intervalobj);
        console.log("time out");
        return {};
    }, 3600*parseInt(timeout));

    var intervalobj = setInterval(function() {
        console.log("I'm busy.");
    }, parseInt(interval));

}

