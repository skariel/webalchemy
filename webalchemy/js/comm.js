debug = false;
message= function (s) {
    if (debug) {
        console.log('sending message:');
        console.log(s);
    }
    ws.send(s)
}
rpcfy= function () {
    var s=''
    s+= arguments.length
    for (var i = 0; i < arguments.length; i++) {
        var si= arguments[i].toString()
        s+= ','+si.length
    }
    for (var i = 0; i < arguments.length; i++) {
        var si= arguments[i].toString()
        s+= ','+si
    }
    return s
}    
rpc= function () {
    message('rpc: '+rpcfy.apply(this,arguments))
}
init_communication = function() {
    ws = new ReconnectingWebSocket(__SOCKET_URL__);
    ws.onopen = function() {
       if (overlay_shown)
            location.reload();
       message('hi, my ID is:'+get_cookie('webalchemy')+': and my tabid is:'+window.name+': and my vendor prefix is:'+vendor_prefix);
    };
    ws.onclose = function() {
      if (!overlay_shown) {
        document.body.appendChild(overlay);
        overlay_shown = true;
      }
    }
    ws.onmessage = function (evt) {
       if (debug) {
          console.log('message received:');
          console.log(evt.data);
       }
       eval.apply(window, [evt.data]);
       message('done');
    };
    (function loop() {
        var rand = Math.round(Math.random() * 9000) + 20000;
        setTimeout(function() {
                message('heartbeat');
                loop();
        }, rand);
    }());
}
