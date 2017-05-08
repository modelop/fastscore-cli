
import sys
import json

from fastscore import Sensor
from fastscore import FastScoreError

def add(connect, name, descfile=None, verbose=False, **kwargs):
    try:
        if descfile:
            with open(descfile) as f:
                desc = f.read()
        else:
            desc = sys.stdin.read()
        sensor = Sensor(name, json.loads(desc))
    except Exception as e:
        raise FastScoreError("Unable to add sensor '%s'" % name, caused_by=e)
    mm = connect.lookup('model-manage')
    updated = sensor.update(mm)
    if verbose:
        print "Sensor updated" if updated else "Sensor created"

def show(connect, name, **kwargs):
    mm = connect.lookup('model-manage')
    sensor = mm.sensors[name]
    print json.dumps(sensor.desc, indent=2)

def remove(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    del mm.sensors[name]
    if verbose:
        print "Sensor removed"

def roster(connect, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    for x in mm.sensors.names():
        print x

def install(connect, name, verbose=False, **kwargs):
    pass

def uninstall(connect, tapid, verbose=False, **kwargs):
    pass

def inspect(connect, tapid=None, **kwargs):
    pass

def points(connect, **kwargs):
    pass

