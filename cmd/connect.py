
import requests

import fastscore

def main(args):
  prefix = args["url-prefix"]
  r = requests.get(prefix + "/1/swagger", verify=False)
  swagger = r.json()
  assert swagger["info"]["title"] == "Connect API"
  with open(".fastscore", "w") as f:
    f.write("connect-prefix: %s\n" % prefix)
  fastscore.conf["connect-prefix"] = prefix
  print "Connect API: ok"

