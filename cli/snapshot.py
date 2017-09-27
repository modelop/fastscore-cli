
import json

from tabulate import tabulate

def roster(connect,
           model_name,
           since=None,
           until=None,
           count=None,
           verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    model = mm.models[model_name]
    snaps = model.snapshots.browse(since, until, count)
    if not verbose:
        for snap in snaps:
            print snap.id
    else:
        t = [ [x.id,model_name,x.created_on,x.stype,x.size] for x in snaps ]
        if len(t) > 0:
            print tabulate(t, headers=["Id","Model","Date/Time","Type","Size"])
        else:
            print "No snapshots found"

def show(connect, model_name, snap_id, asjson=False, **kwargs):
    mm = connect.lookup('model-manage')
    model = mm.models[model_name]
    snap = model.snapshots[snap_id]
    if asjson:
        print json.dumps(snap.to_dict(), indent=2)
    else:
        print "id:         {}".format(snap.id)
        print "created-on: {}".format(snap.created_on)
        print "stype:      {}".format(snap.stype)
        print "size:       {}".format(snap.size)

def restore(connect, model_name, snap_id=None, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    model = mm.models[model_name]
    if snap_id == None:
        snaps = model.snapshots.browse(count=1)
        if len(snaps) == 0:
            print "No snapshots found"
        snap_id = snaps[0].id
    engine = connect.lookup('engine')
    model.snapshots[snap_id].restore(engine)
    if verbose:
        print "Model state restored"

def remove(connect, model_name, snap_id, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    model = mm.models[model_name]
    del model.snapshots[snap_id]
    if verbose:
        print "Snapshot '{}' removed".format(snap_id)

