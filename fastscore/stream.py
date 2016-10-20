
import os
import json

import service

def list(args):
  code,body = service.get("model-manage", "/1/stream")
  if code == 200:
    for x in json.loads(body):
      print x
  else:
    raise Exception(body)

def add(args):
  name = args["stream-name"]
  resource = args["desc-file"]
  if not os.path.exists(resource):
    raise Exception("%s not found" % resource)
  with open(resource) as f:
    desc = f.read()
    ctype = "application/json"
    code,body = service.put("model-manage", "/1/stream/%s" % name, ctype, desc)
    if code == 201:
      print "Stream '%s' added" % name
    elif code == 204:
      print "Stream '%s' updated" %  name
    else:
      raise Exception(body)

def show(args):
  name = args["stream-name"]
  code,body = service.get("model-manage", "/1/stream/%s" % name)
  if code == 200:
    print body,
  elif code == 404:
    print "Stream '%s' not found" % name
  else:
    raise Exception(body)

def sample(args):
  name = args["stream-name"]
  n = int(args["num-items"]) if "num-items" in args else 10
  code,body = service.get("model-manage", "/1/stream/%s" % name)
  if code == 200:
    sample1(n, body)
  elif code == 404:
    print "Stream '%s' not found" % name
  else:
    raise Exception(body)

def sample1(n, desc):
  code,body,ctype = service.post_with_ct("engine", "/1/stream/sample?n=%d" % n,
                                         ctype="application/json", data=desc)
  if code == 200:
    if ctype == "application/json":
      print json.dumps(json.loads(body), indent=2)
    else:
      print body
  else:
    print code
    raise Exception(body)

def remove(args):
  name = args["stream-name"]
  code,body = service.delete("model-manage", "/1/stream/%s" % name)
  if code == 404:
    raise Exception("Stream '%s' not found" % name)
  elif code == 204:
    print "Stream '%s' removed" % name
  else:
    raise Exception(body)

