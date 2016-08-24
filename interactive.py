
import readline
import thread
import ssl
from websocket import create_connection
import json

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
      x = json.loads(ws.recv())
      t = x["topic"]
      m = x["message"]
      print explain(t, m)
  thread.start_new_thread(notify, ())

def explain(t, m):
  if t == "notify" and m["type"] == "health":
    return "[notify] %s is %s" % (m["name"],"DOWN" if m["dir"] == "down" else "up")
  elif t == "log":
    return "[%s] %s [%s] %s" % (m["src"],m["time"],level_text(m["level"]),m["text"])
  else:
    return json.dumps(m, indent=2)

def level_text(l):
  if   l == 128: return "debug"
  elif l == 64:  return "info"
  elif l == 32:  return "notice"
  elif l == 16:  return "warning"
  elif l == 8:   return "error"
  elif l == 4:   return "critical"
  else:          return str(l)

