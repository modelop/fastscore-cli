
def watch(connect, **kwargs):
    pneumo = connect.pneumo()
    try:
        while True:
            print pneumo.recv()
    except KeyboardInterrupt:
        pneumo.close

def flush(connect, **kwargs):
    raise FastScoreError("Not implemented")

def wait(connect, msg_type=None, **kwargs):
    raise FastScoreError("Not implemented")

