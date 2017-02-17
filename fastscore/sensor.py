
import os
import sys
import json

import service

def list(args):
  code,body = service.get("model-manage", "/1/sensor")
  if code == 200:
    for x in json.loads(body.decode('utf-8')):
      print x
  else:
    raise Exception(body.decode('utf-8'))

def add(args):
  name = args["sensor-name"]
  if "desc-file" in args:
    resource = args["desc-file"]
    if not os.path.exists(resource):
      raise Exception("%s not found" % resource)
    with open(resource) as f:
      desc = f.read()
  else:
    desc = sys.stdin.read()
  ctype = "application/json"
  code,body = service.put("model-manage", "/1/sensor/%s" % name, ctype, desc)
  if code == 201:
    print "Sensor '%s' added" % name
  elif code == 204:
    print "Sensor '%s' updated" %  name
  else:
    raise Exception(body.decode('utf-8'))

def show(args):
  name = args["sensor-name"]
  code,body = service.get("model-manage", "/1/sensor/%s" % name)
  if code == 200:
    print body.decode('utf-8'),
  elif code == 404:
    print "Sensor '%s' not found" % name
  else:
    raise Exception(body.decode('utf-8'))

def remove(args):
  name = args["sensor-name"]
  code,body = service.delete("model-manage", "/1/sensor/%s" % name)
  if code == 404:
    raise Exception("Sensor '%s' not found" % name)
  elif code == 204:
    print "Sensor '%s' removed" % name
  else:
    raise Exception(body.decode('utf-8'))

