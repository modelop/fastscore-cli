
from fastscore import Sensor

class JetStable(object):

    def __init__(self, engine):
        self._engine = engine
        self._sensors = {}

    def track(self, sandbox):
        tap1 = 'jet.' + sandbox + '.input.records.count'
        tap2 = 'jet.' + sandbox + '.output.records.count'

        sid1 = Sensor.prep(tap1).install(self._engine)
        sid2 = Sensor.prep(tap2).install(self._engine)

        self._sensors[sandbox] = [sid1,sid2]

    def untrack(self, sandbox):
        self._engine.clear()
        for sid in self._sensors.pop(sandbox):
            self._engine.active_sensors[sid].uninstall()

    def untrackall(self):
        self._engine.clear()
        for ss in self._sensors.values():
            for sid in ss:
                self._engine.active_sensors[sid].uninstall()
        self._sensors = {}

