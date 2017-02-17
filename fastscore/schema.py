
import os
import sys
import json

import service

def list(args):
  code,body = service.get("model-manage", "/1/schema")
  if code == 200:
    for x in json.loads(body.decode('utf-8')):
      print x
  else:
    raise Exception(body.decode('utf-8'))

def add(args):
  name = args["schema-name"]
  if "schema-file" in args:
    resource = args["schema-file"]
    if not os.path.exists(resource):
      raise Exception("%s not found" % resource)
    with open(resource) as f:
      schema = f.read()
  else:
    schema = sys.stdin.read()
  ctype = "application/json"
  code,body = service.put("model-manage", "/1/schema/%s" % name, ctype, schema)
  if code == 201:
    print "Schema '%s' added" % name
  elif code == 204:
    print "Schema '%s' updated" %  name
  else:
    raise Exception(body.decode('utf-8'))

def show(args):
  name = args["schema-name"]
  code,body = service.get("model-manage", "/1/schema/%s" % name)
  if code == 200:
    print body.decode('utf-8'),
  elif code == 404:
    print "Schema '%s' not found" % name
  else:
    raise Exception(body.decode('utf-8'))

def remove(args):
  name = args["schema-name"]
  code,body = service.delete("model-manage", "/1/schema/%s" % name)
  if code == 404:
    raise Exception("Schema '%s' not found" % name)
  elif code == 204:
    print "Schema '%s' removed" % name
  else:
    raise Exception(body.decode('utf-8'))

