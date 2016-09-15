
import json

def begin():
  global count, total
  count = 0
  total = 0

def action(datum):
  global count, total
  count += 1
  o = json.loads(datum)
  total += o["prime"]
  if False:
    yield "0"

def end():
  global count, total
  yield str(count)
  yield str(total)

