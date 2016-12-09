
import os
import yaml
import requests

API_NAMES = ["engine","model-manage","engine-x"]

options = {
  "verbose": 0
}

preferred = {}    # preferred API instance names (set with -<api>:<name>)
resolved = {}     # API instance prefixes

if os.path.exists(".fastscore"):
  with open(".fastscore", "r") as f:
    options = yaml.load(f)

def proxy_prefix():
  if not "proxy-prefix" in options:
    raise(Exception("Not connected - use 'fastscore connect <url-prefix>'"))
  return options["proxy-prefix"]

def head(api, path):
  r = requests.head(lookup(api) + path, verify=False)
  return r.status_code,r.headers

def get(api, path):
  r = requests.get(lookup(api) + path, verify=False)
  return r.status_code,r.content

def get_str(api, path):
  r = requests.get(lookup(api) + path, verify=False)
  return r.status_code,r.content

def get_with_ct(api, path):
  r = requests.get(lookup(api) + path, verify=False)
  ctype = r.headers["content-type"]
  return r.status_code,r.content,ctype

def put(api, path, ctype, data):
  headers = {"content-type": ctype}
  r = requests.put(lookup(api) + path, headers=headers, data=data, verify=False)
  return r.status_code,r.content

def put_with_headers(api, path, headers, data):
  r = requests.put(lookup(api) + path, headers=headers, data=data, verify=False)
  return r.status_code,r.content

def put_multi(api, path, parts):
  r = requests.put(lookup(api) + path, files=parts, verify=False)
  return r.status_code,r.content

def post(api, path, ctype=None, data=None):
  headers = {"content-type": ctype} if ctype != None else None
  r = requests.post(lookup(api) + path, headers=headers, data=data, verify=False)
  return r.status_code,r.content

def post_with_ct(api, path, ctype=None, data=None):
  headers = {"content-type": ctype} if ctype != None else None
  r = requests.post(lookup(api) + path, headers=headers, data=data, verify=False)
  ctype = r.headers["content-type"]
  return r.status_code,r.content,ctype

def delete(api, path):
  r = requests.delete(lookup(api) + path, verify=False)
  return r.status_code,r.content

def lookup(api):
  if api in resolved:
    return resolved[api]
  if api in preferred:
    name = preferred[api]
    prefix = proxy_prefix() + "/api/1/service/%s" % name
    r = requests.get(prefix + "/1/health", verify=False)
    if r.status_code != 200:
      raise(Exception("%s is not healthy" % name))
    resolved[api] = prefix
    return prefix
  else:
    r = requests.get(proxy_prefix() + "/api/1/service/connect/1/connect?api=%s" % api, verify=False)
    if r.status_code != 200:
      raise(Exception(r.text))
    fleet = r.json()
    if len(fleet) == 0:
      raise(Exception("%s not found" % api))
    for x in fleet:
      if x["health"] == "ok":
        prefix = proxy_prefix() + "/api/1/service/%s" % x["name"]
        resolved[api] = prefix
        return prefix
    raise(Exception("No healthy instances found"))

# This records the first occurance of the engine api
# to .fastscore, which is what we will use by default. 
def set_fleet(data):
    config = yaml.load(data)
    fleet = config['fastscore']['fleet']
    with open('.fastscore', 'a') as f:
        for ship in fleet:
            if ship['api'] == 'engine-x':
                f.write("engine-api: %s\n" % 'engine-x')
                break
            elif ship['api'] == 'engine':
                f.write("engine-api: %s\n" % 'engine')
                break

# Added to resolve ambiguity between engine and engine-x.
# engine-api is recorded in .fastscore.
def engine_api_name():
    if 'engine-x' in resolved:
        return 'engine-x'
    elif 'engine' in resolved:
        return 'engine'
    if 'engine-x' in preferred:
        return 'engine-x'
    elif 'engine' in preferred:
        return 'engine'
    if 'engine-api' in options:
        return options['engine-api']
    raise(Exception('No engine found'))

