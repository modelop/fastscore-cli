
import json

def watch(connect, **kwargs):
    pneumo = connect.pneumo.socket()
    try:
        while True:
            msg = pneumo.recv()
            print msg
    except KeyboardInterrupt:
        pneumo.close

def history(connect, verbose=True, asjson=True, **kwargs):
    history = connect.pneumo.history(asjson=asjson)
    if asjson:
        print json.dumps(history, indent=2)
    else:
        for msg in history:
            print msg

