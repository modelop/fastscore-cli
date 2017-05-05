
from os.path import exists

import yaml

def set(connect, config_file, **kwargs):
    try:
        with open(config_file) as f:
            reconf = connect.configure(yaml.load(f))
            if reconf:
                print "(Re)configured"
            else:
                print "Configured"
    except Exception as e:
        raise FastScoreError("Unable to configure FastScore", caused_by=e)

def show(connect, **kwargs):
    config = connect.get_config()
    if config:
        print config
    else:
        print "FastScore not configured (use 'fastscore config set')"

