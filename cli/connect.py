
from os.path import expanduser

from fastscore.suite import Connect

def connect(proxy_prefix, **kwargs):
    co = Connect(proxy_prefix)
    savefile = expanduser('~/.fastscore')
    co.dump(savefile)
    print "Connected"

def fleet(connect, **kwargs):
    pass

def use(name, connect, **kwargs):
    pass

