
import sys
from time import sleep

import requests

from service import options, proxy_prefix, cookies, RELEASE
from tabulate import tabulate

from version import BUILD_DATE

def main(args):
  fleet_path = proxy_prefix() + "/api/1/service/connect/1/connect"
  if options["wait"]:
    sys.stdout.write("Waiting...")
    sys.stdout.flush()
    while True:
      r = requests.get(fleet_path, cookies=cookies(), verify=False)
      if r.status_code == 200 and all([ x["health"] == "ok" for x in r.json() ]):
        print " done"
        break
      sys.stdout.write(".")
      sys.stdout.flush()
      sleep(0.5)
  else:
    r = requests.get(fleet_path, cookies=cookies(), verify=False)

  if r.status_code == 403:
    print "Connect not configured"
  elif r.status_code == 200:
    t = [ [x["name"],x["api"],x["health"]] for x in r.json() ]
    print tabulate(t, headers=["Name","API","Health"])
  else:
    raise Exception(r.text)

def version(args):
  uv = [["CLI","UI","ok",RELEASE,BUILD_DATE]]
  cv = connect_ver()
  sv = service_ver()
  t = uv + cv
  if sv != None:
    t += sv
  print tabulate(t, headers=["Name","API","Health","Release","Built On"])
  if sv == None:
    print "Other services not configured"

def connect_ver():
  r = requests.get(proxy_prefix() + "/api/1/service/connect/1/health",
                      cookies=cookies(), verify=False)
  if r.status_code == 200:
    x = r.json()
    return [["connect","connect","ok",x["release"],x["built_on"]]]
  else:
    raise Exception(r.text)

def service_ver():
  r = requests.get(proxy_prefix() + "/api/1/service/connect/1/connect",
                      cookies=cookies(), verify=False)
  if r.status_code == 403:
    return None
  elif r.status_code == 200:
    return [ [x["name"],x["api"],x["health"],x["release"],x["built_on"]] for x in r.json() ]
  else:
    raise Exception(r.text)

