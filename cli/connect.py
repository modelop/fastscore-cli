
import sys
import json
from os.path import expanduser
from time import sleep
from fastscore.suite import Connect
from fastscore.errors import FastScoreError
from .version import BUILD_DATE
from . import __version__
from .colors import tcol

from tabulate import tabulate

def connect(proxy_prefix, verbose=False, nowait=False, **kwargs):
    connect = Connect(proxy_prefix)
        
    if not nowait:
        if verbose:
            sys.stdout.write("Waiting...")
            sys.stdout.flush()
        while True:
            try:
                connect.check_health()
                if verbose:
                    print
                break
            except FastScoreError as e:
                if (hasattr(e.caused_by, 'status') and e.caused_by.status == 401):
                    savefile = expanduser('~/.fastscore')
                    connect.dump(savefile)
                    raise e
                if verbose:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                sleep(0.5)
            except:
                if verbose:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                sleep(0.5)
    savefile = expanduser('~/.fastscore')
    connect.dump(savefile)
    if verbose:
        print "Connected to FastScore proxy at %s" % proxy_prefix

def fleet(connect, verbose=False, asjson=False, wait=False, **kwargs):
    if wait:
        if verbose and not asjson:
            sys.stdout.write("Waiting...")
            sys.stdout.flush()
        while True:
            try:
                xx = connect.fleet()
                if all([ x.health == 'ok' for x in xx ]):
                    if verbose and not asjson:
                        print "done"
                    break
                if verbose and not asjson:
                    sys.stdout.write(':')
            except:
                if verbose and not asjson:
                    sys.stdout.write('.')
            sleep(0.5)
    else:
        xx = connect.fleet()
    def paintok(x):
        return tcol.OKGREEN + x + tcol.ENDC if x == 'ok' \
          else tcol.FAIL + x + tcol.ENDC
    if verbose:
        y = connect.check_health()
        if asjson:
            doc = [{'name': 'CLI',
                    'api': 'UI',
                    'health': 'ok',
                    'release': __version__,
                    'built_on': BUILD_DATE},
                   {'name': 'connect',
                    'api': 'connect',
                    'health': 'ok',
                    'release': y.release,
                    'built_on': y.built_on}] + map(lambda x: x.to_dict(), xx)
            print json.dumps(doc, indent=2)
        else:
            t = [["CLI","UI",paintok("ok"),__version__,BUILD_DATE],
                 ["connect","connect",paintok("ok"),y.release,y.built_on]]
            t += [ [x.name,x.api,paintok(x.health),x.release,x.built_on] for x in xx ]
            print tabulate(t, headers=["Name","API","Health","Release","Built On"])
    else:
        if asjson:
            doc = map(lambda x: x.to_dict(), xx)
            print json.dumps(doc, indent=2)
        else:
            t = [ [x.name,x.api,paintok(x.health)] for x in xx ]
            print tabulate(t, headers=["Name","API","Health"])

def use(connect, name=None, verbose=False, **kwargs):
    if name:
        x = connect.get(name)
        connect.target = x
        if verbose:
            print "'%s' set as a preferred instance of '%s'" % (name,x.api)
            print "Subsequent commands to target '%s'" % name
    else:
        if verbose:
            if connect.target:
                print "Current target instance is '%s'" % connect.target.name
            else:
                print "Target instance not selected"
        else:
            if connect.target:
                print connect.target.name

