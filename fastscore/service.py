
import os
import yaml
import requests

options = {}

if os.path.exists(".fastscore"):
  with open(".fastscore", "r") as f:
    options = yaml.load(f)

def connect_prefix():
  if not "connect-prefix" in options:
    raise(Exception("Not connected - use 'fastscore connect <url-prefix>'"))
  return options["connect-prefix"]

def get(api, path):
  _,host,port = lookup(api)
  r = requests.get("https://%s:%d%s" % (host,port,path), verify=False)
  return r.status_code,r.content

def get_str(api, path):
  _,host,port = lookup(api)
  r = requests.get("https://%s:%d%s" % (host,port,path), verify=False)
  return r.status_code,r.content

def get_with_ct(api, path):
  _,host,port = lookup(api)
  r = requests.get("https://%s:%d%s" % (host,port,path), verify=False)
  ctype = r.headers["content-type"]
  return r.status_code,r.content,ctype

def put(api, path, ctype, data):
  _,host,port = lookup(api)
  headers = {"content-type": ctype}
  r = requests.put("https://%s:%d%s" % (host,port,path),
                      headers=headers, data=data, verify=False)
  return r.status_code,r.content

def put_multi(api, path, parts):
  _,host,port = lookup(api)
  r = requests.put("https://%s:%d%s" % (host,port,path), files=parts, verify=False)
  return r.status_code,r.content

def post(api, path, ctype=None, data=None):
  _,host,port = lookup(api)
  headers = {"content-type": ctype} if ctype != None else None
  r = requests.post("https://%s:%d%s" % (host,port,path),
                  headers=headers, data=data, verify=False)
  return r.status_code,r.content

def post_with_ct(api, path, ctype=None, data=None):
  _,host,port = lookup(api)
  headers = {"content-type": ctype} if ctype != None else None
  r = requests.post("https://%s:%d%s" % (host,port,path),
                  headers=headers, data=data, verify=False)
  ctype = r.headers["content-type"]
  return r.status_code,r.content,ctype

def delete(api, path):
  _,host,port = lookup(api)
  r = requests.delete("https://%s:%d%s" % (host,port,path), verify=False)
  return r.status_code,r.content

def lookup(api):
  if api in options:
    return options[api]
  r = requests.get(connect_prefix() + "/1/connect?api=%s" % api, verify=False)
  if r.status_code != 200:
    raise(Exception(r.text))
  fleet = r.json()
  if len(fleet) == 0:
    raise(Exception("%s not found" % api))
  for x in fleet:
    if x["health"] == "ok":
      trio = x["name"],x["host"],x["port"]
      options[api] = trio
      return trio
  raise(Exception("No healthy instances found"))

