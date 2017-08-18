
def pause(connect, verbose=False, **kwargs):
    engine = connect.lookup('engine')
    engine.pause()
    if verbose:
        print "Engine '%s' paused" % engine.name

def unpause(connect, verbose=False, **kwargs):
    engine = connect.lookup('engine')
    engine.unpause()
    if verbose:
        print "Engine '%s' unpaused" % engine.name

def reset(connect, verbose=False, **kwargs):
    engine = connect.lookup('engine')
    engine.reset()
    if verbose:
        print "Engine '%s' reset" % engine.name

