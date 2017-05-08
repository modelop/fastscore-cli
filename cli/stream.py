
import sys

from fastscore import Stream
from fastscore import FastScoreError

def add(connect, name, descfile=None, verbose=False, **kwargs):
    try:
        if descfile:
            with open(descfile) as f:
                desc = f.read()
        else:
            desc = sys.stdin.read()
    except Exception as e:
        raise FastScoreError("Unable to add stream '%s'" % name, caused_by=e)
    stream = Stream(name, desc)
    mm = connect.lookup('model-manage')
    updated = stream.update(mm)
    if verbose:
        print "Stream updated" if updated else "Stream created"

def show(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    stream = mm.streams[name]
    sys.stdout.write(stream.desc)
    sys.stdout.flush()

def remove(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    del mm.streams[name]
    if verbose:
        print "Stream removed"

def roster(connect, **kwargs):
    mm = connect.lookup('model-manage')
    for x in mm.streams.names():
        print x

def attach(connect, slot, verbose=False, **kwargs):
    pass

def detach(connect, slot, verbose=False, **kwargs):
    pass

