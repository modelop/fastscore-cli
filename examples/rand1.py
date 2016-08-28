
import random

def begin():
  print "*BEGIN*"
  yield '"output-1"'
  yield '"output-2"'
  yield '"output-3"'

def action(datum):
  yield str(random.random())

def end():
  print "*END*"
  yield "1.23"
  yield "2.34"
  yield "3.45"

