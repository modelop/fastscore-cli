
import sys
from os.path import exists, expanduser
import yaml
import iso8601

from fastscore.suite import Connect
from fastscore.errors import FastScoreError

import connect, config

COMMAND_HELP = [
  ("help",       "Explain commands and options"),
  ("connect",    "Establish a FastScore connection"),
  ("config",     "Configure FastScore fleet"),
  ("fleet",      "Examine status of FastScore fleet"),
  ("use",        "Select a target instance"),
  ("model",      "Manage analytic models"),
  ("attachment", "Manage model attachments"),
  ("snapshot",   "Manage model snapshots"),
  ("stream",     "Manage streams/stream descriptors"),
  ("sensor",     "Manage sensors/sensor descriptors"),
  ("stats",      "Show various statistics"),
  ("pneumo",     "Listen for Pneumo messages")
]

def help_header():
    print "FastScore CLI v1.5"

def overview_commands(**kwargs):
    help_header()
    print "Usage: fastscore <command> [<subcommand> ...]"
    print "Available commands:"
    for cmd,desc in COMMAND_HELP:
        print "  %-16s" % cmd, desc
    print "Use 'help <command>' to get more details on a <command> usage"

def explain_options(**kwargs):
    help_header()
    print "Options:"
    print "  -v                   be verbose"
    print "  -type:<model-type>   set model type (ignore file extension)"
    print "  -type:pfa-json       --- PFA (json)"
    print "  -type:pfa-pretty     --- PrettyPFA"
    print "  -type:pfa-yaml       --- PFA (yaml)"
    print "  -type:python         --- Python"
    print "  -type:python3        --- Python 3"
    print "  -type:r              --- R"
    print "  -count:NNN           list no more than NNN items"
    print "  -since:DATETIME      show items created after DATETIME (iso8601)"
    print "  -until:DATETIME      show items created before DATETIME (iso8601)"
    print "  -wait                wait for an operation to complete"

def explain_command(cmd, **kwargs):
    explain_command1(cmd)

COMMAND_PATTERNS = [
    (overview_commands, []),
    (overview_commands, ["help"]),
    (explain_options,   ["help","options"]),
    (explain_command,   ["help","<cmd>"]),
    (connect.connect,   ["connect","<proxy_prefix>"]),
    (config.set,        ["config","set","<config_file>"]),
    (config.show,       ["config","show"]),
    (connect.fleet,     ["fleet"]),
    (connect.use,       ["use","<instance_name>"])
]

def explain_command1(cmd):
    x = [ desc for cmd1,desc in COMMAND_HELP if cmd1 == cmd ]
    if x == []:
      print "Command '%s' not available (use 'help')" % cmd
    else:
        print "%s:" % x[0]
        for _,pat in COMMAND_PATTERNS:
          if len(pat) > 0 and pat[0] == cmd:
            print " ", str.join(" ", pat)

def main():
    (words,opts) = parse_opts(sys.argv[1:])
    for cmd,pat in COMMAND_PATTERNS:
        args = reduce(match, zip(words, pat), []) if len(words) == len(pat) else None
        if args != None:
            try:
                if len(words) == 0 or words[0] == 'help' or words[0] == 'connect':
                    cmd(*args, **opts)
                else:
                    savefile = expanduser("~/.fastscore")
                    if exists(savefile):
                        co = Connect.load(savefile)
                        cmd(co, *args, **opts)
                        co.dump(savefile)
                    else:
                        raise FastScoreError("Not connected (use 'fastscore connect')")
                return 0
            except FastScoreError as e:
                print e
                print
                return 1
    print "Use 'fastscore help' or 'fastscore help <command>'"
    return 0

def parse_opts(args):
    opts = {}
    for x in args:
        if x == "-v":
            opts['verbose'] = True
        elif x == '-wait':
            opts['wait'] = True
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

