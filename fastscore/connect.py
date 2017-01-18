
import sys

import requests
from time import sleep

import service

def main(args):
  prefix = args["url-prefix"]
  connect_health = prefix + "/api/1/service/connect/1/health"

  if service.options["wait"]:
    sys.stdout.write("Connecting...")
    sys.stdout.flush()
    while True:
      try:
        r = requests.get(connect_health, verify=False)
        if r.status_code == 200:
          break
        progress_char = ":"
      except requests.ConnectionError:
        progress_char = "."
      sys.stdout.write(progress_char)
      sys.stdout.flush()
      sleep(0.5)
    print " done"
  else:
    r = requests.get(prefix, verify=False)
    assert r.status_code == 200

  with open(".fastscore", "w") as f:
    f.write("proxy-prefix: %s\n" % prefix)
  service.options["proxy-prefix"] = prefix
  print "Proxy prefix set"

