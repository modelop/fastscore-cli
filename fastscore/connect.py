
import requests

import service

def main(args):
  prefix = args["url-prefix"]
  r = requests.get(prefix, verify=False)
  assert r.status_code == 200
  with open(".fastscore", "w") as f:
    f.write("proxy-prefix: %s\n" % prefix)
  service.options["proxy-prefix"] = prefix
  print "Proxy prefix set"

