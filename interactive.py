
import readline
import thread
import ssl
from websocket import create_connection

import fastscore
import dispatch

words = []

def complete(text, state):
  global words, matches
  if state == 0:
    matches = [ w for w in words if w.startswith(text) ]
  if state < len(matches):
    return matches[state]
  return None

def loop():
  if "connect-prefix" in fastscore.conf:
    connect_notify()
    
  readline.set_completer(complete)
  readline.parse_and_bind("tab: complete")
  try:
    while True:
      line = raw_input("> ")
      if line != "":
        if not dispatch.run(line.split()):
          print "Invalid command - use 'help'"
  except EOFError:
    print

def connect_notify():
  prefix = fastscore.conf["connect-prefix"]
  def notify():
    ws = create_connection(prefix.replace("https:", "wss:") + "/1/notify",
                              sslopt={"cert_reqs": ssl.CERT_NONE})
    while True:
      x = ws.recv()
      print x
  thread.start_new_thread(notify, ())
  
