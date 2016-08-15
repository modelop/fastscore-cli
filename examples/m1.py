
import json
from random import expovariate
from math import trunc

def action(datum):
  point = json.loads(datum)
  x,y,z = (point["x"],point["y"],point["z"])
  v = x*x + y*y + z*z

  n = trunc(expovariate(1.0))
  for _ in xrange(n):
    yield json.dumps(v)

