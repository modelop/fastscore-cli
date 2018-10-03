
from threading import Thread
from time import sleep

import re
import json
from fastscore.pneumo import EngineStateMsg, EngineConfigMsg, SensorReportMsg
from fastscore import Sensor, FastScoreError


def memory(connect, verbose=False, **kwargs):
    fmt = lambda data: "%.1fmb" % (data / 1048576.0)
    sensor_trail(connect, 'sys.memory', fmt)

def cpu_utilization(connect, verbose=False, **kwargs):
    fmt = lambda data: "kernel: %.1f user: %.1f" % (data['kernel'],data['user'])
    sensor_trail(connect, 'sys.cpu.utilization', fmt)

def sensor_trail(connect, point, formatter):
    if connect.target == None:
        raise FastScoreError("Target not selected (use 'fascore use')")
    sid = Sensor.prep(point).install(connect.target)
    pneumo = connect.pneumo.socket(src=connect.target.name, type='sensor-report')
    try:
        while True:
            msg = pneumo.recv()
            if msg.sid == sid:
                print "%s: %s" % (msg.src,formatter(msg.data))

    except KeyboardInterrupt:
        pneumo.close()
        connect.target.active_sensors[sid].uninstall()

def jets(connect, verbose=False, **kwargs):

    engine = connect.lookup('engine')
    if engine.active_model == None:
        raise FastScoreError("Model not loaded")

    class JetWatcher(Thread):
        def __init__(self, name, jets, vals):
            self._name = name
            self._jets = jets
            self._vals = vals
            super(JetWatcher, self).__init__()

        def run(self):
            def fmt(v):
                return "{:.1f} rps".format(v) if v != None else '---'
            sleep(1)
            while True:
                x = [ fmt(self._vals[sid1]) + "/" + fmt(self._vals[sid2])
                            for sid1,sid2 in self._jets.values() ]
                print "{}: {}".format(self._name, " ".join(x))
                for sid in self._vals:
                    self._vals[sid] = None
                sleep(2)
                #


    vals = {}
    jets = {}
    REPINT = 1.0

    for jet in engine.active_model.jets:
        itap = 'jet.{}.input.records.count'.format(jet.sandbox)
        sid1 = Sensor.prep(itap, interval=REPINT).install(engine)
        otap = 'jet.{}.output.records.count'.format(jet.sandbox)
        sid2 = Sensor.prep(otap, interval=REPINT).install(engine)
        vals[sid1] = None
        vals[sid2] = None
        jets[jet.sandbox] = (sid1,sid2)
    
    watcher = JetWatcher(engine.name, jets, vals)
    watcher.daemon = True
    watcher.start()

    pneumo = connect.pneumo.socket(src=engine.name)

    try:
        while True:
            msg = pneumo.recv()

            if isinstance(msg, SensorReportMsg):

                if msg.sid in vals:
                    if msg.delta_time:
                        vals[msg.sid] = msg.data / msg.delta_time
                    else:
                        vals[msg.sid] = msg.data / REPINT

            if isinstance(msg, EngineConfigMsg):
                print "change detected"
                print msg.op
                if msg.op == 'start':
                    for jet in engine.active_model.jets:
                        itap = 'jet.{}.input.records.count'.format(jet.sandbox)
                        sid1 = Sensor.prep(itap, interval=REPINT).install(engine)
                        otap = 'jet.{}.output.records.count'.format(jet.sandbox)
                        sid2 = Sensor.prep(otap, interval=REPINT).install(engine)
                        vals[sid1] = None
                        vals[sid2] = None
                        jets[jet.sandbox] = (sid1,sid2)

    except KeyboardInterrupt:
        pneumo.close()
        for sid in vals:
            engine.active_sensors[sid].uninstall()

def streams(connect, verbose=False, **kwargs):
    engine = connect.lookup('engine')
    if engine.active_model == None:
        raise FastScoreError("Model not loaded")

    class StreamWatcher(Thread):
        def __init__(self, name, streams, values):
            self._name = name
            self._streams = streams
            self._values = values
            super(StreamWatcher, self).__init__()

        def run(self):
            def fmt(v):
                return "{:.1f} rps".format(v) if v != None else '---'
            sleep(1)
            while True:
                x = [ "{}:{}".format(slot, fmt(self._values[sid]))
                                for slot,sid in self._streams.items() ]
                print "{}: {}".format(self._name, " | ".join(x))
                for sid in self._values:
                    self._values[sid] = None
                sleep(2)

    streams = {}
    values = {}
    REPINT = 1.0

    for x in engine.active_model.slots:
        tap = 'manifold.{}.records.count'.format(x.slot)
        sid = Sensor.prep(tap, interval=REPINT).install(engine)
        values[sid] = None
        streams[x.slot] = sid

    watcher = StreamWatcher(engine.name, streams, values)
    watcher.daemon = True
    watcher.start()

    pneumo = connect.pneumo.socket(src=engine.name, type='sensor-report')
    try:
        while True:
            msg = pneumo.recv()
            if msg.sid in values:
                values[msg.sid] = msg.data / REPINT

    except KeyboardInterrupt:
        pneumo.close()
        for sid in values:
            engine.active_sensors[sid].uninstall()

