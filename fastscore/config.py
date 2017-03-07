
import os
import requests

from service import proxy_prefix, cookies

def show(args):
  r = requests.get(proxy_prefix() + "/api/1/service/connect/1/config",
                      cookies=cookies(), verify=False)
  if r.status_code == 200:
    print r.text,
  elif r.status_code == 404:
    raise Exception("No configuration set")
  else:
    raise Exception(r.text)

def set(args):
  resource = args["config-file"]
  if not os.path.exists(resource):
    raise Exception("%s not found" % resource)
  with open(resource) as f:
    data = f.read()
    headers = {"content-type": "application/x-yaml"}
    r = requests.put(proxy_prefix() + "/api/1/service/connect/1/config",
          data=data, headers=headers, cookies=cookies(), verify=False)
    if r.status_code == 201:
      print "Configuration set"
    elif r.status_code == 204:
      print "Configuration updated"
    else:
      raise Exception(r.text)

