
from service import options
from service import get, put, delete
from service import engine_api_name

import json
from urllib import quote
from tabulate import tabulate

def list(args):
  model_name = args["model-name"]
  path = "/1/model/%s/snapshot" % model_name

  filters = []
  if "count" in options:
    filters.append("count=%d" % options["count"])
  if "since" in options or "until" in options:
    d1 = options["since"].isoformat() if "since" in options else ""
    d2 = options["until"].isoformat() if "until" in options else ""
    filters.append("date-range=%s--%s" % (quote(d1),quote(d2)))
  if len(filters) > 0:
    path += "?" + "&".join(filters)

  code,body = get("model-manage", path)
  if code == 200:
    t = [ [x["id"],
           model_name,
           x["created_on"],
           x["type"],
           x["size"]] for x in reversed(json.loads(body)) ]
    print tabulate(t, headers = ["Id","Model","Date/Time","Type","Size"])
  else:
    raise Exception(body)

def describe(args):
  model_name = args["model-name"]
  snap_id = args["snap-id"]
  code,body = get("model-manage", "/1/model/%s/snapshot/%s/metadata" % (model_name,snap_id))
  if code == 200:
    print json.dumps(json.loads(body), indent=2)
  elif code == 300:
    print "Snapshot id '%s' is ambiguous" % snap_id
  elif code == 404:
    print "Snapshot not found"
  else:
    raise Exception(body)

def restore(args):
  model_name = args["model-name"]
  snap_id = args["snap-id"] if "snap-id" in args else last_snap_id(model_name)
  code,body = get("model-manage", "/1/model/%s/snapshot/%s/contents" % (model_name,snap_id))
  if code == 200:
    restore1(body)
  elif code == 300:
    print "Snapshot id '%s' is ambiguous" % snap_id
  elif code == 404:
    print "Snapshot not found"
  else:
    raise Exception(body)

def restore1(state):
  code,body = put(engine_api_name(), "/1/job/state", "application/octet-stream", state)
  if code == 204:
    print "Model state restored"
  else:
    raise Exception(body)

def last_snap_id(model_name):
  code,body = get("model-manage", "/1/model/%s/snapshot?count=1" % model_name)
  if code == 200:
    ss = json.loads(body)
    if len(ss) == 0:
      raise Exception("No snapsnots found")
    return ss[0]["id"]
  else:
    raise Exception(body)

def remove(args):
  model_name = args["model-name"]
  snap_id = args["snap-id"]
  code,body = delete("model-manage", "/1/model/%s/snapshot/%s" % (model_name,snap_id))
  if code == 204:
    print "Snapshot deleted"
  elif code == 300:
    print "Snapshot id '%s' is ambiguous" % snap_id
  elif code == 404:
    print "Snapshot not found"
  else:
    raise Exception(body)

