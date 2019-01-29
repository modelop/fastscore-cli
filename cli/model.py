
import sys
import re
import json
from os.path import splitext

from tabulate import tabulate

from fastscore import Model, Sensor, FastScoreError
from fastscore.model import Attachment
from fastscore.v1.rest import ApiException
from .editor import run_editor
from .colors import tcol

from threading import Thread
import readline

KNOWN_MODEL_EXTENSIONS = {
  '.pfa':   'pfa-json',
  '.ppfa':  'pfa-pretty',
  '.json':  'pfa-json',
  '.yaml':  'pfa-yaml',
  '.py':    'python',
  '.py3':   'python3',
  '.R':     'R',
  '.c':     'c',
  '.m':     'octave',
  '.ipynb': 'jupyter',
  '.java':  'java',
}

KNOWN_ANCHORS = [
  ("def\\s+action\(",            'python'),
  ("action\\s+<-\\s+function\(", 'R')
]

def add(connect, name, srcfile=None, mtype=None, verbose=False, **kwargs):
    try:
        if srcfile:
            with open(srcfile) as f:
                source = f.read()
            if mtype == None:
                mtype = model_type_from_file(srcfile)
        else:
            source = sys.stdin.read()
            if mtype == None:
                mtype = model_type_from_source(source)
    except Exception as e:
        raise FastScoreError("Unable to add model '%s'" % name, caused_by=e)
    model = Model(name, mtype, source)
    mm = connect.lookup('model-manage')
    updated = model.update(mm)
    if verbose:
        print "Model updated" if updated else "Model created"

def show(connect, name, edit=False, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    model = mm.models[name]
    if edit:
        source1 = run_editor(model.source, "MODEL_EDITING")
        if source1 != None:
            model.source = source1
            model.update()
            if verbose:
                print "Model updated"
        else:
            if verbose:
                print "No changes (or changes discarded)"
    else:
        sys.stdout.write(model.source)
        sys.stdout.flush()

def roster(connect, asjson=False, **kwargs):
    mm = connect.lookup('model-manage')
    if asjson:
        doc = map(lambda x: x.to_dict(), mm.models)
        print json.dumps(doc, indent=2)
    else:
        t = [ [x.name,x.mtype] for x in mm.models ]
        print tabulate(t, headers=["Name","Type"])

def remove(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    del mm.models[name]
    if verbose:
        print "Model '%s' removed" % name

def verify(connect, name, verbose=False, quiet=False, asjson=False, embedded_schemas={}, **kwargs):
    mm = connect.lookup('model-manage')
    engine = connect.lookup('engine')
    model = mm.models[name]
    try:
        info = engine.load_model(model, embedded_schemas=embedded_schemas, dry_run=True)
        if asjson:
            doc = info.to_dict()
            doc['name']   = model.name
            doc['mtype']  = model.mtype
            doc['sloc'] = model.source.count('\n')
            print json.dumps(doc, indent=2)
        else:
            if verbose:
                sloc = model.source.count('\n')
                t = [[model.name,model.mtype,sloc]]
                print tabulate(t, headers=["Name","Type","SLOC"])
                print

                print_slot_map(info.slots)
                print

                if info.install_libs != []:
                    print "These libraries will be installed: %s." % ", ".join(info.install_libs)
                if info.warn_libs != []:
                    print "WARNING: the model imports %s." % ", ".join(info.warn_libs)
                if info.attach_libs != []:
                    print "Libraries to be found in attachment(s): %s." % ", ".join(info.attach_libs)
                if info.snapshots != 'none':
                    print "The model snapshots mode is '%s'" % info.snapshots

            if not quiet:
                print tcol.OKGREEN + "The model contains no errors" + tcol.ENDC

    except FastScoreError as e:
        # one-line error message
        if isinstance(e.caused_by, ApiException):
            raise FastScoreError(e.caused_by.body)
        else:
            raise e

def load(connect, name, attachment_file=None, verbose=False, embedded_schemas={}, **kwargs):
    mm = connect.lookup('model-manage')
    engine = connect.lookup('engine')
    model = mm.models[name]
    if attachment_file == None:
        engine.load_model(model, embedded_schemas=embedded_schemas)
    else:
        attachment = Attachment("override", datafile=attachment_file)
        engine.load_model(model, attachment_override_list=[ attachment ], force_inline=True, embedded_schemas=embedded_schemas)
    if verbose:
        print "Model loaded"

def inspect(connect, verbose=False, asjson=False, **kwargs):
    engine = connect.lookup('engine')
    if engine.active_model == None:
        if asjson:
            print "null"
        else:
            print "Model not loaded"
    else:
        x = engine.active_model
        sloc = x.source.count('\n')
        if asjson:
            print json.dumps(x.to_dict(), indent=2)
        else:
            t = [[x.name,x.mtype,sloc,x.snapshots]]
            print tabulate(t, headers=["Name","Type","SLOC","Snapshots"])
            print

            print_slot_map(x.slots)
            print

            if len(x.jets) == 0:
                print "No jets started"
            else:
                t = [ [n+1,jet.pid,jet.sandbox] for (n,jet) in enumerate(x.jets) ]
                print tabulate(t, headers=["Jet #","Pid","Sandbox"])

def unload(connect, verbose=False, **kwargs):
    engine = connect.lookup('engine')
    if engine.active_model != None:
        engine.active_model.unload()
        if verbose:
            print "Model unloaded"
    else:
        if verbose:
            print "Model not loaded"

def scale(connect, count, verbose=False, **kwargs):
    try:
        n = int(count)
    except:
        raise FastScoreError("The number of jets must be a non-negative integer")
    engine = connect.lookup('engine')
    engine.scale(n)
    if verbose:
        print "Model scale changed"

###
# This is now called `input_data` and not `input`,
# b/c when converting python2 to python3 with `2to3`,
# `raw_input` gets renamed to `input`, causing a name
# collision 
###
def input_data(connect, slot=None, verbose=False, **kwargs):
    engine = connect.lookup('engine')
    if slot == None:
        slot = 0
    else:
        try:
            slot = int(slot)
        except:
            raise FastScoreError("The slot number must be an integer")
    if slot % 2 == 1:
        raise FastScoreError("{} is an output slot".format(slot))
    try:
        while True:
            data = raw_input()
            if data == '':
                break
            engine.input(data, slot)
    except EOFError:
        pass
    except KeyboardInterrupt:
        pass

def output(connect, slot=None, nowait=False, noexit=False, **kwargs):
    engine = connect.lookup('engine')
    if slot == None:
        slot = 1
    else:
        try:
            slot = int(slot)
        except:
            raise FastScoreError("The slot number must be an integer")
    if slot % 2 == 0:
        raise FastScoreError("{} is an input slot".format(slot))

    if nowait:
        data = engine.output(slot)
        if data != None:
            print data
    else:
        try:
            while True:
                data = engine.output(slot)
                if data != None:
                    print data.decode()
                    if not noexit:
                        break
        except EOFError:
            print tcol.OKBLUE + "(EOF)" + tcol.ENDC
        except KeyboardInterrupt:
            pass

def interact(connect, **kwargs):
    engine = connect.lookup('engine')
    if engine.state != 'RUNNING':
        raise FastScoreError("{} is not running".format(engine.name))

    slots = [ x.slot for x in engine.active_model.slots ]

    by_schema = {}
    for slot in slots:
        point = "manifold.{}.records.rejected.by.schema".format(slot)
        sid = Sensor.prep(point, aggregate='accumulate').install(engine)
        by_schema[sid] = slot
    by_encoding = {}
    for slot in slots:
        point = "manifold.{}.records.rejected.by.encoding".format(slot)
        sid = Sensor.prep(point, aggregate='accumulate').install(engine)
        by_encoding[sid] = slot

    pneumo = connect.pneumo.socket(src=engine.name,
                                   type='sensor-report',
                                   timeout=0.25)
    cur_slot = 0
    try:
        while engine.state == 'RUNNING':
            prompt = '> ' if cur_slot == 0 else '{}> '.format(cur_slot)
            data = raw_input(prompt)
            if data == '':
                pass
            elif data.startswith('~'):
                try:
                    new_slot = int(data[1:])
                    if new_slot in slots and new_slot % 2 == 0:
                        cur_slot = new_slot
                except:
                    pass
            else:
                engine.input(data, cur_slot)

            try:
                while True:
                    msg = pneumo.recv()
                    if msg.sid in by_schema:
                        for x in msg.data:
                            s =  "REJECTED-By-Schema:{}: {}".format(by_schema[msg.sid], x)
                            print tcol.FAIL + s + tcol.ENDC
                    if msg.sid in by_encoding:
                        for x in msg.data:
                            s = "REJECTED-By-Encoding:{}: {}".format(by_encoding[msg.sid], x)
                            print tcol.FAIL + s + tcol.ENDC
            except:
                pass

            for slot in slots:
                if slot % 2 == 1:
                    data = engine.output(slot)
                    if data != None:
                        s = data if slot == 1 else "[{}] {}".format(slot, data)
                        print tcol.OKGREEN + s.decode() + tcol.ENDC

    except EOFError:
        print
    except KeyboardInterrupt:
        pass

    pneumo.close()
    for sid in by_encoding:
        engine.active_sensors[sid].uninstall()
    for sid in by_schema:
        engine.active_sensors[sid].uninstall()

def print_slot_map(slots):
    def stars(schema):
        if schema == None:
            return "-"
        s = json.dumps(schema)
        return s if len(s) <= 10 else "*****"

    def yesno(flag):
        return "Yes" if flag else "No"

    def glue(a, b):
        if len(a) > len(b):
            b += [[None] * 3] * (len(a) - len(b))
        elif len(a) < len(b):
            a += [[None] * 4] * (len(b) - len(a))
        return [ x + [None] + y for x,y in zip(a, b) ]

    left = [ [x.slot,stars(x.schema),x.action,yesno(x.recordsets)]
                for x in slots if x.slot % 2 == 0 ]
    right = [ [x.slot,stars(x.schema),yesno(x.recordsets)]
                for x in slots if x.slot % 2 == 1 ]
    headers = ["Slot","Schema","Action","Recordsets","","Slot","Schema","Recordsets"]
    print tabulate(glue(left, right), headers=headers)

def model_type_from_file(srcfile):
    _,ext = splitext(srcfile)
    if not ext in KNOWN_MODEL_EXTENSIONS:
        known = ", ".join(KNOWN_MODEL_EXTENSIONS.keys())
        raise FastScoreError("%s must have a proper extension (%s)" % (srcfile,known))
    return KNOWN_MODEL_EXTENSIONS[ext]

def model_type_from_source(source):
    for pat,mtype in KNOWN_ANCHORS:
        if re.search(pat, source, flags=re.MULTILINE):
            return mtype
    raise FastScoreError("Cannot guess model type (use -type:<model_type>)")
