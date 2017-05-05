
import sys
from os.path import expanduser

from fastscore.suite import Connect
from .version import BUILD_DATE
from . import RELEASE

from tabulate import tabulate

def connect(proxy_prefix, **kwargs):
    co = Connect(proxy_prefix)
    savefile = expanduser('~/.fastscore')
    co.dump(savefile)
    print "Connected"

def fleet(connect, verbose=False, wait=False, **kwargs):
    if wait:
        sys.stdout.write("Waiting...")
        sys.stdout.flush()
        while True:
            try:
                xx = connect.fleet()
                if all([ x.health == 'ok' for x in xx ]):
                    print "done"
                    break
                sys.stdout.write(':')
            except:
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

def use(connect, name, **kwargs):
    pass

