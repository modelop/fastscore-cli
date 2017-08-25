
import json

from .colors import tcol

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
            print explain_state(state)
        elif state == "RUNNING":
            print tcol.OKGREEN + state + tcol.ENDC
        else:
            print state

def reset(connect, verbose=False, **kwargs):
    engine = connect.lookup('engine')
    engine.reset()
    if verbose:
        print "Engine '%s' reset" % engine.name

def explain_state(state):
    if state == "INIT":
        return """\
The engine waits until all required streams are attached and the model is loaded."""
    elif state == "RUNNING":
        return """\
The engine is reading data from input streams, passing them to model instances,
collecting outputs from the model, and writing them to output streams."""
    elif state == "PAUSED":
        return """\
No data processing is taking place."""
    elif state == "PIGGING":
        return """\
The engine follows a PIG control record though the data pipeline. Typically, the
state is short-lived."""
    elif state == "FINISHING":
         return """\
All input stream reached EOF but data processing by model instances
continues."""
    elif state == "FINISHED":
         return """\
The data processing is complete. All streams are at EOF. All model instances are
idle. Reset the engine to load another model."""
 
