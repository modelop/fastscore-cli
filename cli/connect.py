
import sys
from os.path import expanduser

from fastscore.suite import Connect
from .version import BUILD_DATE
from . import RELEASE

from tabulate import tabulate

def connect(proxy_prefix, verbose=False, **kwargs):
    co = Connect(proxy_prefix)
    savefile = expanduser('~/.fastscore')
    co.dump(savefile)
    if verbose:
        print "Connected to FastScore proxy at %s" % proxy_prefix

def fleet(connect, verbose=False, wait=False, **kwargs):
    if wait:
        if verbose:
            sys.stdout.write("Waiting...")
            sys.stdout.flush()
        while True:
            try:
                xx = connect.fleet()
                if all([ x.health == 'ok' for x in xx ]):
                    print "done"
                    break
                if verbose:
                    sys.stdout.write(':')
            except:
                if verbose:
                    sys.stdout.write('.')
            sleep(0.5)
    else:
        xx = connect.fleet()
    if verbose:
        y = connect.check_health()
        t = [["CLI","UI","ok",RELEASE,BUILD_DATE],
             ["connect","connect","ok",y.release,y.built_on]]
        t += [ [x.name,x.api,x.health,x.release,x.built_on] for x in xx ]
        print tabulate(t, headers=["Name","API","Health","Release","Built On"])
    else:
        t = [ [x.name,x.api,x.health] for x in xx ]
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

