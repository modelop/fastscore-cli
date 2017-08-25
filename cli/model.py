
import sys
import re
import json

from tabulate import tabulate

from fastscore import Model, FastScoreError
from fastscore.v1.rest import ApiException
from .editor import run_editor
from .colors import tcol

KNOWN_MODEL_EXTENSIONS = {
  '.pfa':  'pfa-json',
  '.ppfa': 'pfa-pretty',
  '.json': 'pfa-json',
  '.yaml': 'pfa-yaml',
  '.py':   'python',
  '.py3':  'python3',
  '.R':    'R',
  '.c':    'c'
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
                mtype = model_type_from_file(srcfile, type)
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

def verify(connect, name, verbose=False, asjson=False, embedded_schemas={}, **kwargs):
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
                
            print tcol.OKGREEN + "The model contains no errors" + tcol.ENDC

    except FastScoreError as e:
        # one-line error message
        if isinstance(e.caused_by, ApiException):
            raise FastScoreError(e.caused_by.body)
        else:
            raise e

def load(connect, name, verbose=False, embedded_schemas={}, **kwargs):
    mm = connect.lookup('model-manage')
    engine = connect.lookup('engine')
    model = mm.models[name]
    engine.load_model(model, embedded_schemas=embedded_schemas)
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

#    engine = connect.lookup('engine')
#    n = int(count)
#    engine.scale(n)
#    if verbose:
#        print "Scaling complete"

def input(connect, **kwargs):
    raise FastScoreError("Not implemented")

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
    return KNOWN_EXTENSION[ext]

def model_type_from_source(source):
    for pat,mtype in KNOWN_ANCHORS:
        if re.search(pat, source, flags=re.MULTILINE):
            return mtype
    raise FastScoreError("Cannot guess model type (use -type:<model_type>)")
