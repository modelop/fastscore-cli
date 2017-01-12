
import os
import yaml
import requests

RELEASE = "1.3"

API_NAMES = ["engine","model-manage","engine-x"]

options = {
  "verbose": 0,
  "wait": False
}

preferred = {}    # preferred API instance names (set with -<api>:<name>)
resolved = {}     # API instance prefixes

if os.path.exists(".fastscore"):
  with open(".fastscore", "r") as f:
    more = yaml.load(f)
    options.update(more)

def proxy_prefix():
  if not "proxy-prefix" in options:
    raise Exception("Not connected - use 'fastscore connect <proxy-prefix>'")
  return options["proxy-prefix"]

def head(name, path, generic=True):
  r = requests.head(lookup(name, generic) + path, verify=False)
  return r.status_code,r.headers

def get(name, path, generic=True):
  r = requests.get(lookup(name, generic) + path, verify=False)
  return r.status_code,r.content

def get_str(name, path, generic=True):
  r = requests.get(lookup(name, generic) + path, verify=False)
  return r.status_code,r.content

def get_with_ct(name, path, generic=True):
  r = requests.get(lookup(name, generic) + path, verify=False)
  ctype = r.headers["content-type"]
  return r.status_code,r.content,ctype

def put(name, path, ctype, data, generic=True):
  headers = {"content-type": ctype}
  r = requests.put(lookup(name, generic) + path, headers=headers, data=data, verify=False)
  return r.status_code,r.content

def put_with_headers(name, path, headers, data, generic=True):
  r = requests.put(lookup(name, generic) + path, headers=headers, data=data, verify=False)
  return r.status_code,r.content

def put_multi(name, path, parts, generic=True):
  r = requests.put(lookup(name, generic) + path, files=parts, verify=False)
  return r.status_code,r.content

def post(name, path, ctype=None, data=None, generic=True):
  headers = {"content-type": ctype} if ctype != None else None
  r = requests.post(lookup(name, generic) + path, headers=headers, data=data, verify=False)
  return r.status_code,r.content

def post_with_ct(name, path, ctype=None, data=None, generic=True):
  headers = {"content-type": ctype} if ctype != None else None
  r = requests.post(lookup(name, generic) + path, headers=headers, data=data, verify=False)
  ctype = r.headers["content-type"] if "content-type" in r.headers else "text/plain"
  return r.status_code,r.content,ctype

def delete(name, path, generic=True):
  r = requests.delete(lookup(name, generic) + path, verify=False)
  return r.status_code,r.content

def lookup(name, generic):
  if generic:
    return lookup_api(name)
  else:
    return proxy_prefix() + "/api/1/service/%s" % name

def lookup_api(api):
  if api in resolved:
    return resolved[api]

  if api in preferred:
    name = preferred[api]
    r = requests.get(proxy_prefix() + "/api/1/service/connect/1/connect?name=%s" % name,
                      verify=False)
    if r.status_code != 200:
      raise Exception(r.text)
    fleet = r.json()
    if len(fleet) == 0:
      raise Exception("%s not configured (use 'fastscore config show')" % name)
    x = fleet[0]
    if x["health"] == "ok":
      prefix = proxy_prefix() + "/api/1/service/%s" % name
      resolved[api] = prefix
      return prefix
    else:
      raise Exception("%s is not healthy" % name)

  else:
    r = requests.get(proxy_prefix() + "/api/1/service/connect/1/connect?api=%s" % api, verify=False)
    if r.status_code != 200:
      raise Exception(r.text)
    fleet = r.json()
    if len(fleet) == 0:
      raise Exception("No instances of '%s' configured (use 'fastscore config show')" % api)
    for x in fleet:
      if x["health"] == "ok":
        prefix = proxy_prefix() + "/api/1/service/%s" % x["name"]
        resolved[api] = prefix
        return prefix
    raise Exception("No healthy instances of '%s' found (use 'fastscore fleet')" % api)

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
    raise Exception("Unable to resolve Engine API (add 'engine-api' option to .fastscore)")

