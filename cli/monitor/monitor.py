
import sys
import time
import re

from fastscore.pneumo import EngineStateMsg, EngineConfigMsg, SensorReportMsg
from fastscore.pneumo import WebSocketTimeoutException

from fastscore import Sensor

from .stable import JetStable

from .terminal import Terminal
from .layout import *
from ..colors import tcol

def monitor(connect, verbose=False, **kwargs):
    engine = connect.lookup('engine')
    stable = JetStable(engine)

    PREINSTALLED_INTERVAL = 2.0

    def draw_engine(name, state):
        if state == "RUNNING":
            s = name + tcol.OKGREEN + " [RUNNING]" + tcol.ENDC
        else:
            s = name + " [" + state + "]"
        return draw(ENGINE_LAYOUT, fixed="Engine:", engine=s)

    def draw_model(model):
        if model == None:
            s = "(not-loaded)"
        else:
            s = model.name + " (" + model.mtype + ")"
        return draw(MODEL_LAYOUT, fixed="Model:", model=s)

    def slot_text(slot):
        if slot % 2 == 0:
            return "I:" + str(slot)
        else:
            return "O:" + str(slot)

    def eof_text(eof):
        return "EOF" if eof else ""

    def rps_text(rps, width):
        return '{:{width},.0f} rps'.format(rps, width=width-4)

    def mbps_text(mbps, width):
        return '{:{width}.1f} mbps'.format(mbps, width=width-5)

    term = Terminal(50)
    l1 = draw_engine(engine.name, engine.state)
    l2 = draw_model(engine.active_model)
    l3 = draw(HEADER_LAYOUT, col1='Stream', col2='', col3='')
    l4 = draw(HEADER_LAYOUT, col1='Jet', col2='Input', col3='Output')
    
    term.insert('roof', "=" * term.max_width)
    term.insert('engine', l1)
    term.insert('model',  l2)
    term.insert('spacer1', "")
    term.insert('header1', l3)
    term.insert('delim1', "-" * term.max_width)

    for slot,x in engine.active_streams.items():
        l = draw(STREAM_LAYOUT, name=x.name,
                                slot=slot_text(slot),
                                eof=eof_text(x.eof),
                                rps='-', mbps='-')
        term.insert(('stream',slot), l)

    term.insert('spacer2', "")
    term.insert('header2', l4)
    term.insert('delim1', "-" * term.max_width)

    if engine.active_model != None:
        name = engine.active_model.name
        for x in engine.active_model.jets:
            stable.track(x.sandbox)
            l = draw(JET_LAYOUT, name=engine.active_model.name,
                                 eof=eof_text(False),
                                 input='-', output='-')
            term.insert(('jet',x.sandbox), l)

    term.insert('cellar', "")

    pneumo = connect.pneumo.socket()
    try:
        while True:
            msg = pneumo.recv()

            if msg.src != engine.name:
                continue    # multiple engines

            engine.clear()

            if isinstance(msg, EngineStateMsg):
                l = draw_engine(msg.src, msg.state.upper())
                term.update('engine', l)
                if msg.state == 'init':
                    # engine reset
                    term.update('model', draw_model(None))
                    term.remove_by_tag('stream')
                    term.remove_by_tag('jet')
                    stable.untrackall()

            elif isinstance(msg, EngineConfigMsg):
                if msg.item == 'model':
                    l = draw_model(engine.active_model)
                    term.update('model', l)

                elif msg.item == 'stream':
                    slot = msg.ref
                    if msg.op == 'detach':
                        term.remove(('stream',slot))
                    else:
                        info = engine.active_streams[slot]
                        l = draw(STREAM_LAYOUT, name=info.name,
                                                slot=slot_text(slot),
                                                eof=eof_text(info.eof),
                                                rps='-', mbps='-')
                        if msg.op == 'attach':
                            term.insert(('stream',slot), l, 'spacer2')
                        elif msg.op == 'reattach':
                            term.update(('stream',slot), l)

                elif msg.item == 'jet':
                    engine.clear()
                    sandbox = msg.ref
                    if msg.op == 'start':
                        stable.track(sandbox)
                        l = draw(JET_LAYOUT, name=engine.active_model.name,
                                 eof=eof_text(False),
                                 input='-', output='-')
                        term.insert(('jet',sandbox), l, 'cellar')

                    elif msg.op == 'stop':
                        term.remove(('jet',sandbox))
                        stable.untrack(sandbox)

            elif isinstance(msg, SensorReportMsg):
                m = re.match('jet\\.(\\d+)\\.(input|output)\\.records\\.count', msg.point)
                if m != None:
                    sandbox = m.group(1)
                    io = m.group(2)
                    (pos,width) = field(io, JET_LAYOUT)
                    if msg.delta_time:
                        rps = msg.data / msg.delta_time
                    else:
                        rps = msg.data / Sensor.DEFAULT_INTERVAL
                    term.update(('jet',sandbox), rps_text(rps, width), pos=pos)
                else:
                    m = re.match('manifold\\.(\\d+)\\.records\\.(count|size)', msg.point)
                    if m != None:
                        slot = int(m.group(1))
                        if m.group(2) == 'count':
                            if msg.delta_time:
                                rps = msg.data / msg.delta_time
                            else:
                                rps = msg.data / PREINSTALLED_INTERVAL
                            (pos,width) = field('rps', STREAM_LAYOUT)
                            term.update(('stream',slot), rps_text(rps, width), pos=pos)
                        else: #size
                            if msg.delta_time:
                                mbps = msg.data / msg.delta_time / 1048576.0
                            else:
                                mbps = msg.data / PREINSTALLED_INTERVAL / 1048576.0
                            (pos,width) = field('mbps', STREAM_LAYOUT)
                            term.update(('stream',slot), mbps_text(mbps, width), pos=pos)

    except KeyboardInterrupt:
        print
        stable.untrackall()

