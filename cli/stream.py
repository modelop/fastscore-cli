
import sys
import json
from base64 import b64decode
from string import printable
from binascii import b2a_hex
from re import match

from fastscore import Stream
from fastscore import FastScoreError

def add(connect, name, descfile=None, verbose=False, **kwargs):
    try:
        if descfile:
            with open(descfile) as f:
                desc = f.read()
        else:
            desc = sys.stdin.read()
        stream = Stream(name, json.loads(desc))
    except Exception as e:
        raise FastScoreError("Unable to add stream '%s'" % name, caused_by=e)
    mm = connect.lookup('model-manage')
    updated = stream.update(mm)
    if verbose:
        print "Stream updated" if updated else "Stream created"

def show(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    stream = mm.streams[name]
    sys.stdout.write(json.dumps(stream.desc, indent=2))
    sys.stdout.flush()

def remove(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    del mm.streams[name]
    if verbose:
        print "Stream removed"

def roster(connect, verbose=False, **kwargs):
    ##TODO: verbose output - add transport type    
    mm = connect.lookup('model-manage')
    for x in mm.streams.names():
        print x

def sample(connect, name, count=None, **kwargs):
    mm = connect.lookup('model-manage')
    stream = mm.streams[name]
    engine = connect.lookup('engine')
    args = [engine]
    if count:
        args.append(int(count))
    sample = map(b64decode, stream.sample(*args))
    if all([ istext(x) for x in sample ]):
        for i,x in enumerate(sample):
            print "%4d: %s" % (i + 1,x)
    else:

##   1: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  0123456701234567
##      01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01

        for i,x in enumerate(sample):
            chunks = [ x[s:s + 16] for s in range(0, len(x), 16) ]
            if chunks == []:
                print "%4d: (empty)"
            else:
                print "%4d: %s  %s" % (i,hex_pane(chunks[0]),str_pane(chunks[0]))
                for y in chunks[1:]:
                    print "      %s  %s" % (hex_pane(y),str_pane(y))

def istext(s):
    return all([ x in printable for x in s ])

def hex_pane(s):
    x = [ b2a_hex(s[i]) if i < len(s) else "  " for i in range(16) ]
    return " ".join(x)

def str_pane(s):
    x = [ s[i] if i < len(s) and s[i] in printable else '.' for i in range(16) ]
    return "".join(x)

def attach(connect, name, slot, verbose=False, **kwargs):
    try:
        (d,n) = parse_slot(slot)
    except Exception as e:
        print e
        raise FastScoreError("Malformed slot (use 'in:1' or 'input' or 'o:3' or 'out')")
    mm = connect.lookup('model-manage')
    stream = mm.streams[name]
    engine = connect.lookup('engine')
    if d:
        engine.inputs[n] = stream
    else:
        engine.outputs[n] = stream
    if verbose:
        print "Stream attached"

def detach(connect, slot, verbose=False, **kwargs):
    try:
        (d,n) = parse_slot(slot)
    except:
        raise FastScoreError("Malformed slot (use 'in:1' or 'input' or 'o:3' or 'out')")
    mm = connect.lookup('model-manage')
    engine = connect.lookup('engine')
    if d:
        del engine.inputs[n]
    else:
        del engine.outputs[n]
    if verbose:
        print "Stream detached"

def parse_slot(slot):
    (g0,_,g2) = match('([a-z]+)(:([0-9]+))?$', slot).groups()
    n = int(g2) if g2 else 1
    if 'input'.startswith(g0):
        return (True,n)
    assert 'output'.startswith(g0)
    return (False,n)
 
