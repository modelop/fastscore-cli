
import sys
import traceback

from fastscore import service, connect, config, fleet, model, attachment
from fastscore import snapshot, stream, sensor, tap, schema, job, pneumo, stats
from fastscore import interactive

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import iso8601

is_interactive = False

command_desc = \
 {"help":         "Explain commands and options",
  "connect":      "Establish FastScore connection",
  "config":       "Configure FastScore",
  "fleet":        "Check FastScore status",
  "model":        "Add/remove models",
  "attachment":   "Add/remove model attachments",
  "snapshot":     "List/restore/remove model snapshots",
  "stream":       "Adds/remove stream descriptors",
  "sensor":       "Add/remove sensor descriptors",
  "schema":       "Add/remove Avro schemas",
  "job":          "Run models",
  "pneumo":       "Listen for notifications",
  "tap":          "Install/remove sensors"}

def help_me(args):
  if "command" in args:
    cmd = args["command"]
    if cmd == "options":
      explain_options()
    else:
      explain_command(cmd)
  else:
    overview_commands()

def help_header():
  print "FastScore CLI v1.5"

command_specs = \
 [(help_me,             ["help"]),
  (help_me,             ["help","<command>"]),
  (connect.main,        ["connect","<url-prefix>"]),
  (connect.main,        ["connect","<url-prefix>","<sec-creds>"]),
  (config.set,          ["config","set","<config-file>"]),
  (config.show,         ["config","show"]),
  (fleet.main,          ["fleet"]),
  (fleet.version,       ["fleet","version"]),
  (model.list,          ["model","list"]),
  (model.add,           ["model","add","<model-name>"]),
  (model.add,           ["model","add","<model-name>","<source-file>"]),
  (model.show,          ["model","show","<model-name>"]),
  (model.remove,        ["model","remove","<model-name>"]),
  (attachment.list,     ["attachment","list","<model-name>"]),
  (attachment.upload,   ["attachment","upload","<model-name>","<att-file>"]),
  (attachment.download, ["attachment","download","<model-name>","<att-name>"]),
  (attachment.remove,   ["attachment","remove","<model-name>","<att-name>"]),
  (snapshot.list,       ["snapshot","list","<model-name>"]),
  (snapshot.describe,   ["snapshot","describe","<model-name>","<snap-id>"]),
  (snapshot.restore,    ["snapshot","restore","<model-name>","<snap-id>"]),
  (snapshot.restore,    ["snapshot","restore","<model-name>"]),
  (snapshot.remove,     ["snapshot","remove","<model-name>","<snap-id>"]),
  (stream.list,         ["stream","list"]),
  (stream.add,          ["stream","add","<stream-name>"]),
  (stream.add,          ["stream","add","<stream-name>","<desc-file>"]),
  (stream.show,         ["stream","show","<stream-name>"]),
  (stream.sample,       ["stream","sample","<stream-name>"]),
  (stream.sample,       ["stream","sample","<stream-name>","<num-items>"]),
  (stream.rate,         ["stream","rate","<stream-name>"]),
  (stream.remove,       ["stream","remove","<stream-name>"]),
  (stream.attach,       ["stream","attach","<stream-name>","<slot>"]),
  (stream.detach,       ["stream","detach","<slot>"]),
  (sensor.list,         ["sensor","list"]),
  (sensor.add,          ["sensor","add","<sensor-name>"]),
  (sensor.add,          ["sensor","add","<sensor-name>","<desc-file>"]),
  (sensor.show,         ["sensor","show","<sensor-name>"]),
  (sensor.remove,       ["sensor","remove","<sensor-name>"]),
  (tap.install,         ["tap","install","<instance-name>","<sensor-name>"]),
  (tap.inspect,         ["tap","inspect","<instance-name>","<tap-id>"]),
  (tap.uninstall,       ["tap","uninstall","<instance-name>","<tap-id>"]),
  (tap.list,            ["tap","list","<instance-name>"]),
  (tap.available,       ["tap","available","<instance-name>"]),
  (schema.list,         ["schema","list"]),
  (schema.add,          ["schema","add","<schema-name>"]),
  (schema.add,          ["schema","add","<schema-name>","<schema-file>"]),
  (schema.show,         ["schema","show","<schema-name>"]),
  (schema.remove,       ["schema","remove","<schema-name>"]),
  (job.run,             ["job","run","<model-name>","<in-stream-name>","<out-stream-name>"]),
  (job.run,             ["job","run","<model-name>","<in-stream-name>"]),
  (job.scale,           ["job","scale","<num-jets>"]),
  (job.cpu_utilization, ["job","cpu-utilization"]),
  (job.cpu_utilization, ["job","cpu-utilization","<duration>"]),
  (job.input,           ["job","input","json"]),
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

def explain_command(cmd):
  if not cmd in command_desc:
    print "Command '%s' not available (use 'help')" % cmd
  else:
    print command_desc[cmd]
    for (_,spec) in command_specs:
      if spec[0] == cmd:
        print " ", str.join(" ", spec)

def overview_commands():
  help_header()
  print "Available commands ('help <command>' for more info):"
  for cmd in sorted(command_desc.keys()):
    print "  %-16s" % cmd, command_desc[cmd]
  print "Use 'help options' to list available options"

def explain_options():
  help_header()
  print "Options:"
  print "  -v                   Verbose (-vv, -vvv)"
  print "  -<api>:<name>        Choose API instance (e.g. -engine:engine-1)"
  print "  -type:<model-type>   Set model type (ignore file extension)"
  print "  -type:pfa-json       --- PFA (json)"
  print "  -type:pfa-pretty     --- PrettyPFA"
  print "  -type:pfa-yaml       --- PFA (yaml)"
  print "  -type:h2o-java       --- H2O (java)"
  print "  -type:python         --- Python"
  print "  -type:python3        --- Python 3"
  print "  -type:r              --- R"
  print "  -type:java           --- Java"
  print "  -type:c              --- C"
  print "  -count:NNN           list no more than NNN items"
  print "  -since:DATE          show items created after DATETIME (iso8601)"
  print "  -until:DATE          show items created before DATETIME (iso8601)"
  print "  -wait                Wait for a job to complete"

def interpret_options(words):
  global is_interactive
  for x in words:
    if x == '-v':
      service.options["verbose"] = 1
    elif x == '-vv':
      service.options["verbose"] = 2
    elif x == '-vvv':
      service.options["verbose"] = 3
    elif x == '-wait':
      if is_interactive:
        print "Option -wait ignored for interactive sessions"
      else:
        service.options["wait"] = True
    elif x.startswith("-count:"):
      try:
        service.options["count"] = int(x.split(":")[1])
      except ValueError:
        print "Option '%s' ignored" % x
    elif x.startswith("-since:"):
      try:
        service.options["since"] = iso8601.parse_date(x.split(":")[1])
      except:
        print "Option '%s' ignored" % x
    elif x.startswith("-until:"):
      try:
        service.options["until"] = iso8601.parse_date(x.split(":")[1])
      except:
        print "Option '%s' ignored" % x
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
          if hasattr(e, 'message'):
            e = e.message
          if e == "":
            traceback.print_exc()   # Debug only
          else:
            if service.options["verbose"] == 3:
              traceback.print_exc()
            print e
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
  if is_interactive:
    print "Use 'help' or 'help <command>'"
  else:
    print "Use 'fastscore help' or 'fastscore help <command>'"

