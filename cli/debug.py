
from fastscore import Sensor

def manifold(connect, verbose=False, asjson=False, **kwargs):
    debug_tap(connect, 'manifold.debug')

def stream(connect, slot, verbose=False, asjson=False, **kwargs):
    debug_tap(connect, 'manifold.{}.debug'.format(slot))

def debug_tap(connect, point):
    engine = connect.lookup('engine')
    sid = Sensor.prep(point, aggregate=None, interval=0.0).install(engine)
    pneumo = connect.pneumo.socket(src=engine.name, type='sensor-report')
    try:
        while True:
            msg = pneumo.recv()
            if msg.sid == sid:
                when = msg.timestamp.strftime("%X.%f")[:-3]
                print "{}: {}".format(when, msg.data)
    except KeyboardInterrupt:
        pneumo.close()
        engine.active_sensors[sid].uninstall()

