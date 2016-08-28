
import random

def begin():
  print "*BEGIN*"
  yield '"output-1"'
  yield '"output-2"'
  yield '"output-3"'

def action(datum):
  if False:
    yield str(random.random())

