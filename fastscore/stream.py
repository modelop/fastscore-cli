
import os
import sys
import json

import service
from service import engine_api_name

from tabulate import tabulate

def list(args):
  code,body = service.get("model-manage", "/1/stream")
  if code == 200:
    for x in json.loads(body.decode('utf-8')):
      print x
  else:
    raise Exception(body.decode('utf-8'))

def add(args):
  name = args["stream-name"]
  if "desc-file" in args:
    resource = args["desc-file"]
    if not os.path.exists(resource):
      raise Exception("%s not found" % resource)
    with open(resource) as f:
      desc = f.read()
  else:
    desc = sys.stdin.read()
  ctype = "application/json"
  code,body = service.put("model-manage", "/1/stream/%s" % name, ctype, desc)
  if code == 201:
    print "Stream '%s' added" % name
  elif code == 204:
    print "Stream '%s' updated" %  name
  else:
    raise Exception(body.decode('utf-8'))

def show(args):
  name = args["stream-name"]
  code,body = service.get("model-manage", "/1/stream/%s" % name)
  if code == 200:
    print body.decode('utf-8'),
  elif code == 404:
    print "Stream '%s' not found" % name
  else:
    raise Exception(body.decode('utf-8'))

def sample(args):
  name = args["stream-name"]
  n = int(args["num-items"]) if "num-items" in args else 10
  code,body = service.get("model-manage", "/1/stream/%s" % name)
  if code == 200:
    sample1(n, body)
  elif code == 404:
    print "Stream '%s' not found" % name
  else:
    raise Exception(body.decode('utf-8'))

def sample1(n, desc):
  code,body,ctype = service.post_with_ct(engine_api_name(), "/1/stream/sample?n=%d" % n,
                                         ctype="application/json", data=desc)
  if code == 200:
    if ctype == "application/json":
      print json.dumps(json.loads(body.decode('utf-8')), indent=2)
    else:
      print body.decode('utf-8')
  else:
    raise Exception(body.decode('utf-8'))

def rate(args):
  name = args["stream-name"]
  code,body = service.get("model-manage", "/1/stream/%s" % name)
  if code == 200:
    rate1(body)
  elif code == 404:
    print "Stream '%s' not found" % name
  else:
    raise Exception(body.decode('utf-8'))

def rate1(desc):
  code,body = service.post(engine_api_name(), "/1/stream/rate",
                           ctype="application/json", data=desc)
  if code == 200:
    t = [ [n+1,x["rps"]/1000,x["mbps"]] for n,x in enumerate(json.loads(body.decode('utf-8'))) ]
    print tabulate(t, headers=["#","Krec/s","MB/s"])
  else:
    raise Exception(body.decode('utf-8'))

def remove(args):
  name = args["stream-name"]
  code,body = service.delete("model-manage", "/1/stream/%s" % name)
  if code == 404:
    raise Exception("Stream '%s' not found" % name)
  elif code == 204:
    print "Stream '%s' removed" % name
  else:
    raise Exception(body.decode('utf-8'))

