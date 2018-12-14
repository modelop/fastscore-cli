
import sys
import json
from os.path import exists

from tabulate import tabulate

from fastscore import Schema
from fastscore import FastScoreError
from .editor import run_editor
from .colors import tcol

def add(connect, name, schema_file=None, verbose=False, **kwargs):
    try:
        if schema_file:
            with open(schema_file) as f:
                source = f.read()
        else:
            source = sys.stdin.read()
        schema = Schema(name, json.loads(source))
    except Exception as e:
        raise FastScoreError("Unable to add schema '%s'" % name, caused_by=e)
    mm = connect.lookup('model-manage')
    updated = schema.update(mm)
    if verbose:
        print "Schema updated" if updated else "Schema created"

def show(connect, name, edit=False, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    schema = mm.schemata[name]
    if edit:
        text = json.dumps(schema.source, indent=2)
        text1 = run_editor(text, "SCHEMA_EDITING")
        if text1 != None:
            try:
                schema.source = json.loads(text1)
            except:
                raise FastScoreError("Invalid JSON")
            schema.update()
            if verbose:
                print "Schema updated"
        else:
            if verbose:
                print "No changes (or changes discarded)"
    else:
        print json.dumps(schema.source, indent=2)

def remove(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    del mm.schemata[name]
    if verbose:
        print "Schema removed"

def roster(connect, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    if verbose:
        t = [ [x,'Avro'] for x in mm.schemata.names() ]
        print tabulate(t, headers=["Name","Type"])
    else:
        for x in mm.schemata.names():
            print x

def verify(connect, name, data_file=False, verbose=False, **kwargs):
    data = []
    if data_file:
        if not exists(data_file):
            raise FastScoreError("{} not found".format(data_file))
        with open(data_file) as f:
            data = f.readlines()
    mm = connect.lookup('model-manage')
    schema = mm.schemata[name]
    engine = connect.lookup('engine')
    sid = schema.verify(engine)
    if verbose:
        print tcol.OKGREEN + "Schema OK" + tcol.ENDC
    for rec in data:
        rec = rec.strip()
        try:
            engine.verify_data(sid, json.loads(rec))
            sys.stdout.write(tcol.OKGREEN + "OK   " + tcol.ENDC)
            print "{:32}".format(rec)
        except ValueError:  
            sys.stdout.write(tcol.FAIL    + "JSON " + tcol.ENDC)
            print "{:32}".format(rec)
        except FastScoreError as e:
            sys.stdout.write(tcol.FAIL    + "FAIL " + tcol.ENDC)
            print "{:32}".format(rec)
            print "     {}".format(e.message)
        print
    engine.unverify_schema(sid)

