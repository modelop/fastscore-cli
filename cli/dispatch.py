
import sys
from os.path import exists, expanduser
import yaml
import json
import iso8601


from fastscore.suite import Connect
from fastscore.constants import MODEL_CONTENT_TYPES
from fastscore.errors import FastScoreError

from cli import RELEASE

import cli.connect, cli.config, cli.pneumo
import cli.model, cli.attachment, cli.snapshot
import cli.schema, cli.stream, cli.engine
import cli.sensor, cli.stats, cli.policy
import cli.debug, cli.monitor, cli.run

import logging
import urllib3
logging.getLogger(urllib3.__package__).setLevel(logging.ERROR)

from cli.colors import tcol

COMMAND_HELP = [
  ("help",       "Explain commands and options"),
  ("connect",    "Establish a FastScore connection"),
  ("config",     "Configure the FastScore fleet"),
  ("fleet",      "Examine status of the FastScore fleet"),
  ("use",        "Select the target instance"),
  ("run",        "Run easy model setups"),
  ("model",      "Manage analytic models"),
  ("attachment", "Manage model attachments"),
  ("schema",     "Manage Avro schemas"),
  ("snapshot",   "Manage model snapshots"),
  ("policy",     "Manage import policies"),
  ("stream",     "Manage streams/stream descriptors"),
  ("engine",     "Manage engine state"),
  ("sensor",     "Manage sensors/sensor descriptors"),
  ("stats",      "Show assorted statistics"),
  ("debug",      "Watch debugging messages"),
  ("pneumo",     "Access Pneumo messages"),
  ("monitor",    "Monitor data processing"),
]

def help_header():
    print tcol.BOLD + "FastScore CLI v%s" % RELEASE + tcol.ENDC

def overview_commands(**kwargs):
    help_header()
    print "Usage: fastscore <command> [<subcommand> ...]"
    print "Available commands:"
    for cmd,desc in COMMAND_HELP:
        print "  %-16s" % cmd, desc
    print "Run 'fastscore help <command>' to get more " \
                    "details on <command> usage"

def explain_options(**kwargs):
    help_header()
    print "Options:"
    print "  -v                      be verbose"
    print "  -type:<model-type>      set model type (ignore file extension)"
    print "  -type:pfa-json          --- PFA (json)"
    print "  -type:pfa-pretty        --- PrettyPFA"
    print "  -type:pfa-yaml          --- PFA (yaml)"
    print "  -type:python            --- Python"
    print "  -type:python3           --- Python 3"
    print "  -type:R                 --- R"
    print "  -type:c                 --- C"
    print "  -type:octave            --- Octave"
    print "  -count:NNN              list no more than NNN items"
    print "  -since:DATETIME         show items created after DATETIME (iso8601)"
    print "  -until:DATETIME         show items created before DATETIME (iso8601)"
    print "  -schema:<name>:<schema> embed schema when loading a model"
    print "  -json                   output as JSON (handy for scripts)"
    print "  -e                      open item for editing"
    print "  -wait                   wait for operation to complete"
    print "  -m                      monitor engine operations"

def explain_command(cmd, **kwargs):
    explain_command1(cmd)

COMMAND_PATTERNS = [
    (overview_commands,  []),
    (overview_commands,  ["help"]),
    (explain_options,    ["help","options"]),
    (explain_command,    ["help","<cmd>"]),
    (cli.connect.connect, ["connect","<proxy_prefix>"]),
    (cli.config.set,     ["config","set","<config_file>"]),
    (cli.config.show,    ["config","show"]),
    (cli.connect.fleet,  ["fleet"]),
    (cli.connect.use,    ["use","<instance_name>"]),
    (cli.connect.use,    ["use"]),
    (cli.run.run,        ["run","<model_name>","<stream0>","<stream1>"]),
    (cli.run.run,        ["job","run","<model_name>","<stream0>","<stream1>"]),
    (cli.model.add,      ["model","add","<model_name>","<src_file>"]),
    (cli.model.add,      ["model","add","<model_name>"]),
    (cli.model.show,     ["model","show","<model_name>"]),
    (cli.model.roster,   ["model","list"]),
    (cli.model.remove,   ["model","remove","<model_name>"]),
    (cli.model.verify,   ["model","verify","<model_name>"]),
    (cli.model.load,     ["model","load","<model_name>"]),
    (cli.model.inspect,  ["model","inspect"]),
    (cli.model.unload,   ["model","unload"]),
    (cli.model.scale,    ["model","scale","<count>"]),
    (cli.model.input,    ["model","input"]),
    (cli.attachment.roster, ["attachment","list","<model_name>"]),
    (cli.attachment.upload, ["attachment","upload","<model_name>","<file_to_upload>"]),
    (cli.attachment.download, ["attachment","download","<model_name>","<att_name>"]),
    (cli.attachment.remove, ["attachment","remove","<model_name>","<att_name>"]),
    (cli.policy.set,     ["policy","set","<policy_file>"]),
    (cli.policy.set,     ["policy","set"]),
    (cli.policy.show,    ["policy","show"]),
    (cli.schema.add,     ["schema","add","<schema_name>","<schema_file>"]),
    (cli.schema.add,     ["schema","add","<schema_name>"]),
    (cli.schema.show,    ["schema","show","<schema_name>"]),
    (cli.schema.remove,  ["schema","remove","<schema_name>"]),
    (cli.schema.roster,  ["schema","list"]),
    (cli.schema.verify,  ["schema","verify","<schema_name>"]),
    (cli.schema.verify,  ["schema","verify","<schema_name>","<data_file>"]),
    (cli.snapshot.roster, ["snapshot","list","<model_name>"]),
    (cli.snapshot.show,  ["snapshot","show","<model_name>","<snap_id>"]),
    (cli.snapshot.restore, ["snapshot","restore","<model_name>"]),
    (cli.snapshot.restore, ["snapshot","restore","<model_name>","<snap_id>"]),
    (cli.snapshot.remove, ["snapshot","remove","<model_name>","<snap_id>"]),
    (cli.stream.add,     ["stream","add","<stream_name>","<desc_file>"]),
    (cli.stream.add,     ["stream","add","<stream_name>"]),
    (cli.stream.show,    ["stream","show","<stream_name>"]),
    (cli.stream.remove,  ["stream","remove","<stream_name>"]),
    (cli.stream.roster,  ["stream","list"]),
    (cli.stream.inspect, ["stream","inspect","<slot>"]),
    (cli.stream.inspect, ["stream","inspect"]),
    (cli.stream.verify,  ["stream","verify","<stream_name>","<slot>"]),
    (cli.stream.attach,  ["stream","attach","<stream_name>","<slot>"]),
    (cli.stream.detach,  ["stream","detach","<slot>"]),
    (cli.stream.sample,  ["stream","sample","<stream_name>"]),
    (cli.engine.pause,   ["engine","pause"]),
    (cli.engine.unpause, ["engine","unpause"]),
    (cli.engine.inspect, ["engine","inspect"]),
    (cli.engine.reset,   ["engine","reset"]),
    (cli.sensor.add,     ["sensor","add","<sensor_name>","<desc_file>"]),
    (cli.sensor.add,     ["sensor","add","<sensor_name>"]),
    (cli.sensor.show,    ["sensor","show","<sensor_name>"]),
    (cli.sensor.remove,  ["sensor","remove","<sensor_name>"]),
    (cli.sensor.roster,  ["sensor","list"]),
    (cli.sensor.install, ["sensor","install","<sensor_name>"]),
    (cli.sensor.uninstall, ["sensor","uninstall","<tap_id>"]),
    (cli.sensor.inspect, ["sensor","inspect","<tap_id>"]),
    (cli.sensor.inspect, ["sensor","inspect"]),
    (cli.sensor.points,  ["sensor","points"]),
    (cli.stats.memory,   ["stats","memory"]),
    (cli.stats.cpu_utilization, ["stats","cpu-utilization"]),
    (cli.stats.jets,     ["stats","jets"]),
    (cli.stats.streams,  ["stats","streams"]),
    (cli.debug.manifold, ["debug","manifold"]),
    (cli.debug.stream,   ["debug","stream","<slot>"]),
    (cli.pneumo.watch,   ["pneumo"]),
    (cli.pneumo.history, ["pneumo","history"]),
    (cli.monitor.monitor, ["monitor"]),
]

def explain_command1(cmd):
    x = [ desc for cmd1,desc in COMMAND_HELP if cmd1 == cmd ]
    if x == []:
      print "Command '%s' not available (use 'help')" % cmd
    else:
        print x[0]
        print
        for _,pat in COMMAND_PATTERNS:
          if len(pat) > 0 and pat[0] == cmd:
            print "  fastscore " + str.join(" ", pat)

def main():
    (words,opts) = parse_opts(sys.argv[1:])
    for cmd,pat in COMMAND_PATTERNS:
        args = reduce(match, zip(words, pat), []) if len(words) == len(pat) else None
        if args != None:
            try:
                if len(words) == 0 or words[0] == 'help' or words[0] == 'connect':
                    cmd(*args, **opts)
                    return 0
                else:
                    savefile = expanduser("~/.fastscore")
                    if exists(savefile):
                        connect = Connect.load(savefile)
                        cmd(connect, *args, **opts)
                        connect.dump(savefile)

                        if opts['monitor']:
                            cli.monitor.monitor(connect, **opts)
                        return 0
                    else:
                        raise FastScoreError("Not connected (use 'fastscore connect')")

            except FastScoreError as e:
                if opts['asjson']:
                    print json.dumps({'error': str(e)}, indent=2)
                else:
                    print tcol.FAIL + str(e) + tcol.ENDC
                return 1
    print "Use 'fastscore help' or 'fastscore help <command>'"
    return 0

def parse_opts(args):
    opts = {
        'asjson': False,
        'embedded_schemas': {},
        'monitor': False,
    }
    for x in args:
        if x == '-v':
            opts['verbose'] = True
        elif x == '-json':
            opts['asjson'] = True
        elif x.startswith("-type:"):
            mtype = x.split(':')[1]
            if mtype in MODEL_CONTENT_TYPES:
                opts['mtype'] = mtype
            else:
                print "Model type '%s' is unknown" % mtype
        elif x.startswith("-count:"):
            try:
                opts['count'] = int(x.split(':')[1])
            except ValueError:
                print "Option '%s' ignored" % x
        elif x.startswith("-since:"):
            try:
                opts['since'] = iso8601.parse_date(x.split(':')[1])
            except:
                print "Option '%s' ignored" % x
        elif x.startswith('-until:'):
            try:
                opts['until'] = iso8601.parse_date(x.split(':')[1])
            except:
                print "Option '%s' ignored" % x
        elif x.startswith('-schema:'):
            try:
                _,name,what = x.split(':')
                try:
                    data = open(what).read()
                except:
                    data = what
                opts['embedded_schemas'][name] = data
            except:
                print "Option '%s' ignored" % x
        elif x == '-e':
            opts['edit'] = True
        elif x == '-wait':
            opts['wait'] = True
        elif x == '-m':
            opts['monitor'] = True
        elif x[0] == '-':
            print "Unknown option '%s' ignored" % x
    words = [ x for x in args if x[0] != '-' ]
    return (words,opts)

def match(acc, (t,s)):
    if acc == None:
        return None
    if s[0] == '<':
        acc.append(t)
        return acc
    if t == s:
        return acc
    return None

