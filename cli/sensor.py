
import sys
import json

from tabulate import tabulate

from fastscore import Sensor
from fastscore import FastScoreError
from .editor import run_editor

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

def show(connect, name, edit=False, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    sensor = mm.sensors[name]
    if edit:
        desc = json.dumps(sensor.desc, indent=2)
        desc1 = run_editor(desc, "SENSOR_EDITING")
        if desc1 != None:
            try:
                sensor.desc = json.loads(desc1)
            except:
                raise FastScoreError("Invalid JSON")
            sensor.update()
            if verbose:
                print "Sensor updated"
        else:
            if verbose:
                print "No changes (or changes discarded)"
    else:
        print json.dumps(sensor.desc, indent=2)

def remove(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    del mm.sensors[name]
    if verbose:
        print "Sensor removed"

def roster(connect, verbose=False, asjson=False, **kwargs):
    mm = connect.lookup('model-manage')
    if asjson:
        print json.dumps(mm.sensors.names(), indent=2)
    else:
        for x in mm.sensors.names():
            print x

def install(connect, name, verbose=False, **kwargs):
    if not connect.target:
        raise FastScoreError("Target not selected (see 'fastscore use')")
    mm = connect.lookup('model-manage')
    sensor = mm.sensors[name]
    sid = sensor.install(connect.target)
    if verbose:
        print "Sensor installed [%s]" % sid
    else:
        print sid

def uninstall(connect, tapid, verbose=False, **kwargs):
    n = toint(tapid)
    if not connect.target:
        raise FastScoreError("Target not selected (see 'fastscore use')")
    mm = connect.lookup('model-manage')
    sensors = connect.target.active_sensors
    if not n in sensors:
        raise FastScoreError("Sensor id %d not found" % n)
    sensors[n].uninstall()
    if verbose:
        print "Sensor uninstalled"

def inspect(connect, tapid=None, verbose=False, asjson=False, **kwargs):
    if not connect.target:
        raise FastScoreError("Target not selected (see 'fastscore use')")
    sensors = connect.target.active_sensors
    if tapid != None:
        n = toint(tapid)
        if not n in sensors:
            raise FastScoreError("Sensor id %d not found" % n)
        if asjson:
            print json.dumps(sensors[n].to_dict(), indent=2)
        else:
            print "Sensor id %d is attached to '%s' at '%s'." \
                    % (n,sensors[n].tap,connect.target.name)
    elif asjson:
        print json.dumps(map(lambda x: x.to_dict(), sensors.values()), indent=2)
    else:
        if verbose:
            print "Sensors installed at '%s':" % connect.target.name
        t = [ [x.id,x.tap] for x in connect.target.active_sensors.values() ]
        print tabulate(t, headers = ["Id","Tap"])

def points(connect, verbose=False, asjson=False, **kwargs):
    if not connect.target:
        raise FastScoreError("Target not selected (see 'fastscore use')")
    if asjson:
        print json.dumps(connect.target.tapping_points, indent=2)
    else:
        if verbose:
            print "Sensor tapping points at '%s':" % connect.target.name
            for x in connect.target.tapping_points:
                print "  " + x
        else:
            for x in connect.target.tapping_points:
                print x

def toint(tapid):
    try:
        return int(tapid)
    except:
        raise FastScoreError("Invalid sensor id '%s'" % tapid)

