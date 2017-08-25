
from fastscore import Sensor

class JetStable(object):

    INTERVAL = 2.0

    TEMPLATE = {
        'Activate': 'permanent',
        'Aggregate': 'sum',
        'Sink': 'Pneumo',
        'Report': {
           'Interval': INTERVAL
        }
    }

    def __init__(self, engine):
        self._engine = engine
        self._sensors = {}

    def track(self, sandbox):
        desc1 = JetStable.TEMPLATE.copy()
        desc1['Tap'] = 'jet.' + sandbox + '.input.records.count'
        desc2 = JetStable.TEMPLATE.copy()
        desc2['Tap'] = 'jet.' + sandbox + '.output.records.count'

        sid1 = Sensor('', desc1).install(self._engine)
        sid2 = Sensor('', desc2).install(self._engine)

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

