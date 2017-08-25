
import sys
import json
from tabulate import tabulate

from base64 import b64decode
from string import printable
from binascii import b2a_hex
from re import match

from fastscore import Stream
from fastscore import FastScoreError
from .editor import run_editor

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

def show(connect, name, edit=False, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    stream = mm.streams[name]
    if edit:
        desc = json.dumps(stream.desc, indent=2)
        desc1 = run_editor(desc, "STREAM_EDITING")
        if desc1 != None:
            try:
                stream.desc = json.loads(desc1)
            except:
                raise FastScoreError("Invalid JSON")
            stream.update()
            if verbose:
                print "Stream updated"
        else:
            if verbose:
                print "No changes (or changes discarded)"
    else:
        print json.dumps(stream.desc, indent=2)

def remove(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    del mm.streams[name]
    if verbose:
        print "Stream removed"

def roster(connect, verbose=False, asjson=False, **kwargs):
    ##TODO: verbose output - add transport type    
    mm = connect.lookup('model-manage')
    if asjson:
        print json.dumps(mm.streams.names(), indent=2)
    else:
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

def inspect(connect, slot=None, verbose=False, asjson=False, **kwargs):
    n = parse_slot(slot)
    engine = connect.lookup('engine')
    if slot == None:
        if asjson:
            doc = map(lambda x: x.to_dict(), engine.active_streams.values())
            print json.dumps(doc, indent=2)
        else:
            t = [ [x.slot,x.name,transport(x.descriptor),str(x.eof)]
                        for x in engine.active_streams.values() ]
            print tabulate(t, headers=["Slot","Name","Transport","EOF"])
    elif n in engine.active_streams:
        info = engine.active_streams[n]
        if asjson:
            print json.dumps(info.to_dict(), indent=2)
        else:
            t = [[info.slot,info.name,transport(info.descriptor),str(info.eof)]]
            print tabulate(t, headers=["Slot","Name","Transport","EOF"])
    else:
        if asjson:
            print "null"
        else:
            print "No stream attached to slot %s" % slot

def transport(desc):
    transport = desc['Transport']
    return transport['Type'] if isinstance(transport, dict) else transport

def attach(connect, name, slot, verbose=False, **kwargs):
    n = parse_slot(slot)
    mm = connect.lookup('model-manage')
    engine = connect.lookup('engine')
    stream = mm.streams[name]
    stream.attach(engine, n)
    if verbose:
        print "Stream attached"

def detach(connect, slot, verbose=False, **kwargs):
    n = parse_slot(slot)
    mm = connect.lookup('model-manage')
    engine = connect.lookup('engine')
    if n in engine.active_streams:
        engine.active_streams[n].detach()
        if verbose:
            print "Stream detached"
    else:
        if verbose:
            print "No stream attached to slot %s" % slot

def parse_slot(slot):
    if slot == None:
        return None
    try:
        return int(slot)
    except:
        raise FastScoreError("Malformed slot number '%s'" % slot)
 