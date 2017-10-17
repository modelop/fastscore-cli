
import json

from fastscore import Sensor

from tabulate import tabulate

PROFILE_TIME = 5.0

def stream(connect, slot, verbose=False, asjson=False, **kwargs):
    engine = connect.lookup('engine')
    point = 'manifold.{}.profile'.format(slot)
    schedule = {
        'Type': 'regular',
        'Interval': 1.0,
    }
    sid = Sensor.prep(point, activate=schedule).install(engine)
    pneumo = connect.pneumo.socket(src=engine.name, type='sensor-report')
    if verbose:
        print "Collecting data ({:.1f}s)...".format(PROFILE_TIME)
    try:
        while True:
            msg = pneumo.recv()
            if msg.sid == sid:
                show_profile(msg.data, asjson)
                break
    except KeyboardInterrupt:
        pass
    pneumo.close()
    engine.active_sensors[sid].uninstall()

def show_profile(data, asjson):
    if asjson:
        print json.dumps(data, indent=2)
    else:

        #{
        #   u'unwrap_envelope': 0.0,
        #   u'unwrap_envelope_n': 0,
        #   u'wrap_envelope': 0.0,
        #   u'wrap_envelope_n': 0,
        #   u'validate_streaming_n': 0,
        #   u'validate_streaming': 0.0,
        #   u'validate_output_records_n': 86722,
        #   u'validate_output_records': 1.126427,
        #   u'validate_input_records': 1.082062,
        #   u'validate_input_records_n': 86629
        #}

        labels = {
            'unwrap_envelope':          "Unwrap envelope",
            'wrap_envelope':            "Wrap envelope",
            'validate_streaming':       "Validate records (streaming mode)",
            'validate_input_records':   "Validate input records",
            'validate_output_records':  "Validate output records",
            }

        o = []
        for x in labels:
            x1 = x + '_n'
            if data[x1] > 0:
                o.append([labels[x],"{:.3f}".format(data[x]),data[x1]])
        print tabulate(o, headers=["Operation","Time, s","Count"])

