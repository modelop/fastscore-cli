
from fastscore import Sensor, FastScoreError

from fastscore.pneumo import SensorReportMsg

def memory(connect, verbose=False, **kwargs):
    fmt = lambda data: "%.1fmb" % (data / 1048576.0)
    sensor_trail(connect, 'sys.memory', fmt)

def cpu_utilization(connect, verbose=False, **kwargs):
    fmt = lambda data: "kernel: %.1f user: %.1f" % (data['kernel'],data['user'])
    sensor_trail(connect, 'sys.cpu.utilization', fmt)

def model(connect, verbose=False, **kwargs):
    raise FastScoreError("not implemented")

def streams(connect, verbose=False, **kwargs):
    raise FastScoreError("not implemented")

def sensor_trail(connect, point, formatter):
    sid = Sensor.prep(point).install(connect.target)
    pneumo = connect.pneumo.socket()
    try:
        while True:
            msg = pneumo.recv()
            if isinstance(msg, SensorReportMsg) \
               and msg.src == connect.target.name \
               and msg.sid == sid:
                print "%s: %s" % (msg.src,formatter(msg.data))

    except KeyboardInterrupt:
        pneumo.close()
        connect.target.active_sensors[sid].uninstall()


