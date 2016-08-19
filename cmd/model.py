
import os
import json
from tabulate import tabulate

import fastscore

def list(args):
  code,body = fastscore.get("model-manage", "/1/model?return=type")
  if code == 200:
    t = [ [x["name"],x["type"]] for x in json.loads(body) ]
    print tabulate(t, headers=["Name","Type"])
  else:
    raise Exception(body)

def add(args):
  name = args["model-name"]
  resource = args["source-file"]
  if not os.path.exists(resource):
    raise Exception("%s not found" % resource)
  ctype = guess_ctype(resource)
  with open(resource) as f:
    model = f.read()
    code,body = fastscore.put("model-manage", "/1/model/%s" % name, ctype, model)
    if code == 201:
      print "Model '%s' added" % name
    elif code == 204:
      print "Model '%s' updated" %  name
    else:
      raise Exception(body)

def show(args):
  name = args["model-name"]
  code,body = fastscore.get("model-manage", "/1/model/%s" % name)
  if code == 200:
    print body,
  elif code == 404:
    print "Model '%s' not found" % name
  else:
    raise Exception(body)

def remove(args):
  name = args["model-name"]
  code,body = fastscore.delete("model-manage", "/1/model/%s" % name)
  if code == 404:
    raise Exception("Model '%s' not found" % name)
  elif code == 204:
    print "Model '%s' removed" % name
  else:
    raise Exception(body)

def guess_ctype(resource):
  _,ext = os.path.splitext(resource)
  if ext == ".pfa":
    return "application/vnd.pfa+json"
  elif ext == ".json":
    return "application/vnd.pfa+json"
  elif ext == ".ppfa":
    return "application/vnd.ppfa"
  elif ext == ".yaml":
    return "application/x-yaml"
  elif ext == ".py":
    return "application/x-python"
  elif ext == ".R":
    return "application/x-r"
  else:
    raise Exception("%s must have a proper extension (.pfa, .ppfa, .yaml, .py, .R)" % resource)

