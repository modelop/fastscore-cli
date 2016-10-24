
import requests

from service import proxy_prefix
from tabulate import tabulate

def main(args):
  r = requests.get(proxy_prefix() + "/api/1/service/connect/1/connect", verify=False)
  ## Somehow, the proxy does not return 'host' and 'port' elements
  if r.status_code == 403:
    print "Connect not configured"
  elif r.status_code == 200:
    t = [ [x["name"],x["api"],x["health"]] for x in r.json() ]
    print tabulate(t, headers=["Name","API","Health"])
  else:
    raise Exception(r.text)

