
import sys
import traceback

from fastscore import conf
from cmd import connect, config, fleet, model, attachment, stream, job

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def help(args):
  usage()

command_specs = \
 [(help,                ["help"]),
  (connect.main,        ["connect","<url-prefix>"]),
  (config.set,          ["config","set","<config-file>"]),
  (config.show,         ["config","show"]),
  (fleet.main,          ["fleet"]),
  (model.list,          ["model","list"]),
  (model.add,           ["model","add","<model-name>","<source-file>"]),
  (model.show,          ["model","show","<model-name>"]),
  (model.remove,        ["model","remove","<model-name>"]),
  (attachment.list,     ["attachment","list","<model-name>"]),
  (attachment.upload,   ["attachment","upload","<model-name>","<att-file>"]),
  (attachment.download, ["attachment","download","<model-name>","<att-name>"]),
  (attachment.remove,   ["attachment","remove","<model-name>","<att-name>"]),
  (stream.list,         ["stream","list"]),
  (stream.add,          ["stream","add","<stream-name>","<desc-file>"]),
  (stream.show,         ["stream","show","<stream-name>"]),
  (stream.sample,       ["stream","sample","<stream-name>"]),
  (stream.sample,       ["stream","sample","<stream-name>","<num-items>"]),
  (stream.remove,       ["stream","remove","<stream-name>"]),
  (job.run,             ["job","run","<model-name>","<in-stream-name>","<out-stream-name>"]),
  (job.run,             ["job","run","<model-name>","<in-stream-name>"]),
  (job.scale,           ["job","scale","<num-jets>"]),
  (job.status,          ["job","status"]),
  (job.output,          ["job","output"]),
  (job.statistics,      ["job","statistics"]),
  (job.statistics_io,   ["job","statistics","io"]),
  (job.statistics0,     ["job","statistics","reset"]),
  (job.memory,          ["job","memory"])]

def main():
  conf["verbose"] = 0
  for x in sys.argv[1:]:
    if x == '-v':
      conf["verbose"] = 1
    elif x == '-vv':
      conf["verbose"] = 2
    elif x == '-vvv':
      conf["verbose"] = 3
    elif x[0] == '-':
      print "Unknown option '%s' ignored" % x

  words = [ x for x in sys.argv[1:] if x[0] != '-' ]
  for command,spec in command_specs:
    if len(words) == len(spec):
      args = reduce(match, zip(words, spec), {})
      if args != None:
        try:
          command(args)
        except Exception as e:
          traceback.print_exc()   # Debug only
          print e.message
        return 0

  usage()

def match(acc, (t,s)):
  if acc == None:
    return None
  if s[0] == "<":
    acc[s[1:-1]] = t
    return acc
  if t == s:
    return acc
  return None

def usage():
  print "FastScore CLI v1.1"
  print "Usage:"
  for (_,spec) in command_specs:
    print "  fastscore", str.join(" ", spec)

def usage():
  print "FastScore CLI v1.1"
  print "Usage:"
  for (_,spec) in command_specs:
    print "  fastscore", str.join(" ", spec)

