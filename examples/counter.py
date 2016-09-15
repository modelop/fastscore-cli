counter = 0
def action(datum):
  global counter
  counter += 1
  yield str(counter)
