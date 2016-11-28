
import os
import sys
import json
import re
from tabulate import tabulate

import service

def list(args):
  code,body = service.get("model-manage", "/1/model?return=type")
  if code == 200:
    t = [ [x["name"],x["type"]] for x in json.loads(body) ]
    print tabulate(t, headers=["Name","Type"])
  else:
    raise Exception(body)

def add(args):
  name = args["model-name"]
  if "source-file" in args:
    resource = args["source-file"]
    if not os.path.exists(resource):
      raise Exception("%s not found" % resource)
    with open(resource) as f:
      model = f.read()
    ctype = guess_file_ctype(resource)
  else:
    model = sys.stdin.read()
    ctype = guess_model_ctype(model)
  code,body = service.put("model-manage", "/1/model/%s" % name, ctype, model)
  if code == 201:
    print "Model '%s' added" % name
  elif code == 204:
    print "Model '%s' updated" %  name
  else:
    raise Exception(body)

def show(args):
  name = args["model-name"]
  code,body = service.get("model-manage", "/1/model/%s" % name)
  if code == 200:
    print body,
  elif code == 404:
    print "Model '%s' not found" % name
  else:
    raise Exception(body)

def remove(args):
  name = args["model-name"]
  code,body = service.delete("model-manage", "/1/model/%s" % name)
  if code == 404:
    raise Exception("Model '%s' not found" % name)
  elif code == 204:
    print "Model '%s' removed" % name
  else:
    raise Exception(body)

def guess_file_ctype(resource):
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
    raise Exception("%s must have a proper extension (.pfa, .ppfa, .yaml, .py, or .R)" % resource)

def guess_model_ctype(model):
  if re.search("def\\s+action\(", model, flags=re.MULTILINE) != None:
    return "application/x-python"
  if re.search("action\\s+<-\\s+function\(", model, flags=re.MULTILINE) != None:
    return "application/x-r"
  else:
    raise Exception("Error: cannot guess the type of the model")

