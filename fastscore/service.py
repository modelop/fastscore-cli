
import os
import time
import yaml
import requests

RELEASE = "1.5"

API_NAMES = ["engine","model-manage","engine-x"]

options = {
  "engine-api": "engine-x",
  "verbose": 0,
  "wait": False
}

preferred = {}    # preferred API instance names (set with -<api>:<name>)
resolved = {}     # API instance prefixes

if os.path.exists(".fastscore"):
  with open(".fastscore", "r") as f:
    more = yaml.load(f)
    options.update(more)

def update_config():
  with open(".fastscore", "w") as f:
    for x in ["proxy-prefix","auth-secret","engine-api"]:
      if x in options:
        f.write("%s: %s\n" % (x,options[x]))

def proxy_prefix():
  if not "proxy-prefix" in options:
    raise Exception("Not connected - use 'fastscore connect <proxy-prefix>'")
  return options["proxy-prefix"]

def head(name, path, generic=True):
  r = requests.head(lookup(name, generic) + path, cookies=cookies(), verify=False)
  return r.status_code,r.headers

def get(name, path, generic=True):
  jar = cookies()
  r = requests.get(lookup(name, generic) + path, cookies=jar, verify=False)
  return r.status_code,r.content

def get_str(name, path, generic=True):
  r = requests.get(lookup(name, generic) + path, cookies=cookies(), verify=False)
  return r.status_code,r.content

def get_with_ct(name, path, generic=True):
  r = requests.get(lookup(name, generic) + path, cookies=cookies(), verify=False)
  ctype = r.headers["content-type"]
  return r.status_code,r.content,ctype

def put(name, path, ctype, data, generic=True):
  headers = {"content-type": ctype}
  r = requests.put(lookup(name, generic) + path, headers=headers, data=data,
                        cookies=cookies(), verify=False)
  return r.status_code,r.content

def put_with_headers(name, path, headers, data, generic=True):
  r = requests.put(lookup(name, generic) + path, headers=headers, data=data,
                        cookies=cookies(), verify=False)
  return r.status_code,r.content

def put_multi(name, path, parts, generic=True):
  r = requests.put(lookup(name, generic) + path, files=parts,
                        cookies=cookies(), verify=False)
  return r.status_code,r.content

def post(name, path, ctype=None, data=None, generic=True):
  headers = {"content-type": ctype} if ctype != None else None
  r = requests.post(lookup(name, generic) + path, headers=headers, data=data,
                        cookies=cookies(), verify=False)
  return r.status_code,r.content

def post_with_ct(name, path, ctype=None, data=None, generic=True):
  headers = {"content-type": ctype} if ctype != None else None
  r = requests.post(lookup(name, generic) + path, headers=headers, data=data,
                        cookies=cookies(), verify=False)
  ctype = r.headers["content-type"] if "content-type" in r.headers else "text/plain"
  return r.status_code,r.content,ctype

def delete(name, path, generic=True):
  r = requests.delete(lookup(name, generic) + path, cookies=cookies(), verify=False)
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

def reset_auth():
  if "auth-secret" in options:
    del options["auth-secret"]

def set_auth(value):
  options["auth-secret"] = value

def cookies():
  if "auth-secret" in options:
    return {"connect.sid": options["auth-secret"]}
  else:
    return {}

