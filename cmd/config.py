
import os
import requests

from fastscore import connect_prefix

def show(args):
  r = requests.get(connect_prefix() + "/1/config", verify=False)
  if r.status_code == 200:
    print r.text,
  else:
    raise Exception(r.text)

def set(args):
  resource = args["config-file"]
  if not os.path.exists(resource):
    raise(Exception("%s not found" % resource))
  with open(resource) as f:
    data = f.read()
    headers = {"content-type": "application/x-yaml"}
    r = requests.put(connect_prefix() + "/1/config",
          data=data, headers=headers, verify=False)
    if r.status_code == 201:
      print "Configuration set"
    elif r.status_code == 204:
      print "Configuration updated"
    else:
      raise(Exception(r.text))

