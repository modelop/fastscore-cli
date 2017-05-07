
import sys
import re

from tabulate import tabulate

from fastscore import Model, FastScoreError

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
  ("def\\s+action\(",               'python'),
  ("action\\s+<-\\s+function\(",    'R')
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
        if updated:
            print "Model '%s' updated" % name
        else:
            print "Model '%s' created" % name

def show(connect, name, **kwargs):
    mm = connect.lookup('model-manage')
    model = mm.models[name]
    sys.stdout.write(model.source)
    sys.stdout.flush()

def roster(connect, **kwargs):
    mm = connect.lookup('model-manage')
    t = [ [x['name'],x['type']] for x in mm.models ]
    print tabulate(t, headers=["Name","Type"])

def remove(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    del mm.models[name]
    if verbose:
        print "Model '%s' removed" % name

def load(connect, name, **kwargs):
    mm = connect.lookup('model-manage')
    engine = connect.lookup('engine')
    model = mm.models[name]
    engine.load(model)

def inspect(connect, **kwargs):
    pass

def unload(connect, **kwargs):
    pass

def scale(connect, count, **kwargs):
    pass

def input(connect, **kwargs):
    pass

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

