
import sys
import json

from tabulate import tabulate

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
    if not connect.target:
        raise FastScoreError("Target not selected (see 'fastscore use')")
    mm = connect.lookup('model-manage')
    sensor = mm.sensors[name]
    reply = sensor.install(connect.target)
    if verbose:
        print "Sensor installed [%s]" % reply.id
    else:
        print reply.id

def uninstall(connect, tapid, verbose=False, **kwargs):
    if not connect.target:
        raise FastScoreError("Target not selected (see 'fastscore use')")
    mm = connect.lookup('model-manage')
    connect.target.uninstall_sensor(tapid)
    if verbose:
        print "Sensor uninstalled"

def inspect(connect, tapid=None, verbose=False, **kwargs):
    if not connect.target:
        raise FastScoreError("Target not selected (see 'fastscore use')")
    if tapid:
        reply = connect.target.active_sensors[tapid]
        print "Sensor %s attached to '%s'" % (reply.id,reply.tap)
        if reply.permanent:
            print "Sensor is permanently active"
    else:
        if verbose:
            t = [ [x.id,x.tap,x.active] for x in connect.target.active_sensors ]
            print tabulate(t, headers = ["Id","Tap","Active"])
        else:
            for x in connect.target.active_sensors:
                print x.id

def points(connect, **kwargs):
    if not connect.target:
        raise FastScoreError("Target not selected (see 'fastscore use')")
    for x in connect.target.tapping_points:
        print x

