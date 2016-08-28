
import requests

from service import connect_prefix
from tabulate import tabulate

def main(args):
  r = requests.get(connect_prefix() + "/1/connect", verify=False)
  if r.status_code == 403:
    print "Connect not configured"
  elif r.status_code == 200:
    t = [ [x["name"],x["api"],x["host"],x["port"],x["health"]] for x in r.json() ]
    print tabulate(t, headers=["Name","API","Host","Port","Health"])
  else:
    raise Exception(r.text)

