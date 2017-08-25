
import json

def watch(connect, **kwargs):
    pneumo = connect.pneumo.socket()
    try:
        while True:
            msg = pneumo.recv()
            when = msg.timestamp.strftime("%X.%f")[:-3]
            print "%s:%s: %s" % (when,msg.src,str(msg))
    except KeyboardInterrupt:
        pneumo.close

def history(connect, verbose=True, asjson=True, **kwargs):
    history = connect.pneumo.history(asjson=asjson)
    if asjson:
        print json.dumps(history, indent=2)
    else:
        for msg in history:
            print msg

