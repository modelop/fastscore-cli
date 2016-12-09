
import os
import sys
import json
import re
from tabulate import tabulate

import service

# -type:<model-type>
requested_type = None

MODEL_TYPES = ["pfa-json","pfa-pretty","pfa-yaml",
               "python","python3","r",
               "java","scala","erlang"]

MEDIA_TYPES = {
  "application/vnd.fastscore.model-pfa+json":   "pfa-json",
  "application/vnd.fastscore.model-pfa-json":   "pfa-json",
  "application/vnd.fastscore.model-pfa-yaml":   "pfa-yaml",
  "application/vnd.fastscore.model-pfa-pretty": "pfa-pretty",
  "application/vnd.fastscore.model-python":     "python",
  "application/vnd.fastscore.model-python2":    "python",
  "application/vnd.fastscore.model-python3":    "python3",
  "application/vnd.fastscore.model-r":          "r",
  "application/vnd.fastscore.model-java":       "java",
  "application/vnd.fastscore.model-scala":      "scala",
  "application/vnd.fastscore.model-erlang":     "erlang",
  # OBSOLETE - DO NOT USE
  "application/vnd.pfa+json":                   "pfa-json",
  "application/json":                           "pfa-json",
  "application/vnd.ppfa":                       "pfa-pretty",
  "application/x-yaml":                         "pfa-yaml",
  "application/x-python":                       "python",
  "application/x-r":                            "r"
}

KNOWN_EXTENSIONS = {
  ".pfa":  "pfa-json",
  ".ppfa": "pfa-pretty",
  ".json": "pfa-json",
  ".yaml": "pfa-yaml",
  ".py":   "python",
  ".py3":  "python3",
  ".R":    "r"
}

def lookup_ctype(type):
  global MEDIA_TYPES
  for ctype in MEDIA_TYPES:
    if MEDIA_TYPES[ctype] == type:
      return ctype
 
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
    ctype = lookup_ctype(guess_file_type(resource))
  else:
    model = sys.stdin.read()
    ctype = lookup_ctype(guess_model_type(model))
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

def guess_file_type(resource):
  global requested_type, KNOWN_EXTENSIONS
  if requested_type != None:
    return requested_type
  _,ext = os.path.splitext(resource)
  if not ext in KNOWN_EXTENSIONS:
    known = ", ".join(KNOWN_EXTENSIONS.keys())
    raise Exception("%s must have a proper extension (%s)" % (resource,known))
  return KNOWN_EXTENSIONS[ext]

def guess_model_type(model):
  global requested_type
  if requested_type != None:
    return requested_type
  if re.search("def\\s+action\(", model, flags=re.MULTILINE) != None:
    return "python"
  if re.search("action\\s+<-\\s+function\(", model, flags=re.MULTILINE) != None:
    return "r"
  else:
    raise Exception("Error: cannot guess the type of the model (use -type:<model-type>)")

