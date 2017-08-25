
def watch(connect, **kwargs):
    pneumo = connect.pneumo()
    try:
        while True:
            msg = pneumo.recv()
            when = msg.timestamp.strftime("%X.%f")[:-3]
            print "%s:%s: %s" % (when,msg.src,str(msg))
    except KeyboardInterrupt:
        pneumo.close

