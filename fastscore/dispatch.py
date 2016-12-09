
import sys
import traceback

from fastscore import service, connect, config, fleet, model, attachment
from fastscore import stream, schema, job, pneumo, stats
from fastscore import interactive

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

is_interactive = False

def help(args):
  usage()

def explain_options(args):
  print "FastScore CLI v1.3"
  print "Options:"
  print "  -v                   Verbose (-vv, -vvv)"
  print "  -<api>:<name>        Choose API instance (e.g. -engine:engine-1)"
  print "  -type:<model-type>   Set model type (ignore file extension)"
  print "  -type:pfa-json       --- PFA (json)"
  print "  -type:pfa-pretty     --- PrettyPFA"
  print "  -type:pfa-yaml       --- PFA (yaml)"
  print "  -type:python         --- Python"
  print "  -type:python3        --- Python 3"
  print "  -type:r              --- R"

command_specs = \
 [(help,                ["help"]),
  (explain_options,     ["help","options"]),
  (connect.main,        ["connect","<url-prefix>"]),
  (config.set,          ["config","set","<config-file>"]),
  (config.show,         ["config","show"]),
  (fleet.main,          ["fleet"]),
  (model.list,          ["model","list"]),
  (model.add,           ["model","add","<model-name>"]),
  (model.add,           ["model","add","<model-name>","<source-file>"]),
  (model.show,          ["model","show","<model-name>"]),
  (model.remove,        ["model","remove","<model-name>"]),
  (attachment.list,     ["attachment","list","<model-name>"]),
  (attachment.upload,   ["attachment","upload","<model-name>","<att-file>"]),
  (attachment.download, ["attachment","download","<model-name>","<att-name>"]),
  (attachment.remove,   ["attachment","remove","<model-name>","<att-name>"]),
  (stream.list,         ["stream","list"]),
  (stream.add,          ["stream","add","<stream-name>"]),
  (stream.add,          ["stream","add","<stream-name>","<desc-file>"]),
  (stream.show,         ["stream","show","<stream-name>"]),
  (stream.sample,       ["stream","sample","<stream-name>"]),
  (stream.sample,       ["stream","sample","<stream-name>","<num-items>"]),
  (stream.rate,         ["stream","rate","<stream-name>"]),
  (stream.remove,       ["stream","remove","<stream-name>"]),
  (schema.list,         ["schema","list"]),
  (schema.add,          ["schema","add","<schema-name>"]),
  (schema.add,          ["schema","add","<schema-name>","<schema-file>"]),
  (schema.show,         ["schema","show","<schema-name>"]),
  (schema.remove,       ["schema","remove","<schema-name>"]),
  (job.run,             ["job","run","<model-name>","<in-stream-name>","<out-stream-name>"]),
  (job.run,             ["job","run","<model-name>","<in-stream-name>"]),
  (job.scale,           ["job","scale","<num-jets>"]),
  (job.debug,           ["job","debug","<model-name>","<in-stream-name>","<out-stream-name>"]),
  (job.debug,           ["job","debug","<model-name>","<in-stream-name>"]),
  (job.cpu_utilization, ["job","cpu-utilization"]),
  (job.cpu_utilization, ["job","cpu-utilization","<duration>"]),
  (job.input,           ["job","input"]),
  (job.stop,            ["job","stop"]),
  (stats.status,        ["job","status"]),
  (stats.statistics,    ["job","statistics"]),
  (stats.statistics_io, ["job","statistics","io"]),
  (stats.statistics0,   ["job","statistics","reset"]),
  (pneumo.watch,        ["pneumo"]),
  (pneumo.flush,        ["pneumo","flush"]),
  (pneumo.list,         ["pneumo","wait"]),
  (pneumo.wait,         ["pneumo","wait","<message-type>"]),
  (stats.memory,        ["job","memory"])]

def interpret_options(words):
  for x in words:
    if x == '-v':
      service.options["verbose"] = 1
    elif x == '-vv':
      service.options["verbose"] = 2
    elif x == '-vvv':
      service.options["verbose"] = 3
    elif x.startswith("-type:") and x.split(":")[1] in model.MODEL_TYPES:
      model.requested_type = x.split(":")[1]
    elif x[0] == '-' and ":" in x and x[1:].split(":")[0] in service.API_NAMES:
      api,name = x[1:].split(":")
      service.preferred[api] = name
    elif x[0] == '-':
      print "Unknown option '%s' ignored" % x

  return [ x for x in words if x[0] != '-' ]

def main():
  global is_interactive
  words = interpret_options(sys.argv[1:])
  if words == []:
    # for auto-complete
    w = sorted(set([ w for _,spec in command_specs
                       for w in spec
                       if w[0] != '<' ]))
    interactive.words = w
    is_interactive = True
    interactive.loop()
    return 0
  elif not run(words):
    return 1

  return 0 # exit status

def run(words):
  for command,spec in command_specs:
    if len(words) == len(spec):
      args = reduce(match, zip(words, spec), {})
      if args != None:
        try:
          command(args)
          return True
        except Exception as e:
          if e.message == "":
            traceback.print_exc()   # Debug only
          else:
            print e.message
          return False
  usage()
  return True

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
  global is_interactive
  print "FastScore CLI v1.3"
  print "Usage:"
  for (_,spec) in command_specs:
    if not is_interactive:
      print "  fastscore", str.join(" ", spec)
    else:
      print " ", str.join(" ", spec)

