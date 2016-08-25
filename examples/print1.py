
import sys

n = 0
def action(datum):
  global n
  if n < 10:
    print "number:", n
    sys.stdout.flush()
  n = n+1
  if False:
    yield "0"

