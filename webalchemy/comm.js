message= function (s) {
    console.log('sending message:')
    console.log(s)
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
