
import sys
import json
from tabulate import tabulate

from base64 import b64decode
from re import match

from fastscore.utils import format_record, hide

from fastscore import Stream
from fastscore import FastScoreError
from .editor import run_editor
from .colors import tcol

def to_stream(connect, lit_or_name):
    if lit_or_name.find(':') != -1:
        return Stream.expand(lit_or_name)
    else:
        mm = connect.lookup('model-manage')
        return mm.streams[lit_or_name]

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

def show(connect, lit_or_name, edit=False, verbose=False, **kwargs):
    if lit_or_name.find(':') != -1:
        stream = Stream.expand(lit_or_name)
        edit = False
    else:
        mm = connect.lookup('model-manage')
        stream = mm.streams[lit_or_name]
        stream.desc = hide(stream.desc)     # *****
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

def sample(connect, lit_or_name, count=None, **kwargs):
    stream = to_stream(connect, lit_or_name)
    engine = connect.lookup('engine')
    args = [engine]
    if count:
        args.append(int(count))
    sample = map(b64decode, stream.sample(*args))
    for i,x in enumerate(sample, 1):
        print format_record(x, i)

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

def verify(connect, lit_or_name, slot, verbose=False, quiet=False, **kwargs):
    stream = to_stream(connect, lit_or_name)
    n = parse_slot(slot)
    engine = connect.lookup('engine')
    int_desc = stream.attach(engine, n, dry_run=True)
    if verbose:
        print json.dumps(int_desc, indent=2)
    if not quiet:
        print tcol.OKGREEN + "The stream descriptor contains no errors" + tcol.ENDC

def attach(connect, lit_or_name, slot, verbose=False, **kwargs):
    stream = to_stream(connect, lit_or_name)
    n = parse_slot(slot)
    engine = connect.lookup('engine')
    stream.attach(engine, n)
    if verbose:
        print "Stream attached to slot %s" % slot

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
 
