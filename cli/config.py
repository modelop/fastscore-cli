
from os.path import exists

import yaml

from fastscore import FastScoreError

def set(connect, config_file, verbose=False, **kwargs):
    try:
        with open(config_file) as f:
            reconf = connect.configure(yaml.load(f))
            if verbose:
                if reconf:
                    print "Configuration updated"
                else:
                    print "Configuration set"
    except Exception as e:
        raise FastScoreError("Unable to configure FastScore", caused_by=e)

def show(connect, **kwargs):
    config = connect.get_config()
    if config:
        print config
    else:
        print "FastScore not configured (use 'fastscore config set')"

