
import json

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

def inspect(connect, verbose=False, asjson=False, **kwargs):
    engine = connect.lookup('engine')
    if asjson:
        doc = {'state': engine.state}
        print json.dumps(doc, indent=2)
    else:
        state = engine.state
        if verbose:
            print "The current engine state is %s." % state
            print
            if state == "INIT":
                print """\
The engine waits until all required streams are attached and the model is loaded."""
            elif state == "RUNNING":
                print """\
The engine is reading data from input streams, passing them to model instances,
collecting outputs from the model, and writing them to output streams."""
            elif state == "PAUSED":
                print """\
No data processing is taking place."""
            elif state == "PIGGING":
                print """\
The engine follows a PIG control record though the data pipeline. Typically, the
state is short-lived."""
            elif state == "FINISHING":
                print """\
All input stream reached EOF but data processing by model instances
continues."""
            elif state == "FINISHED":
                print """\
The data processing is complete. All streams are at EOF. All model instances are
idle. Reset the engine to load another model."""
        else:
            print state

def reset(connect, verbose=False, **kwargs):
    engine = connect.lookup('engine')
    engine.reset()
    if verbose:
        print "Engine '%s' reset" % engine.name

