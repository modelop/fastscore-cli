
import sys

from fastscore import FastScoreError

def set(connect, policy_file=None, mtype=None, preinstall=False, verbose=False, **kwargs):
    if mtype == None:
        raise FastScoreError("Model type not set (use -type: option)")
    try:
        if policy_file:
            with open(policy_file) as f:
                text = f.read()
        else:
            text = sys.stdin.read()
    except Exception as e:
        raise FastScoreError("Unable to set policy", caused_by=e)
    engine = connect.lookup('engine')
    engine.policy.set('import', mtype, text, preinstall)
    if verbose:
        print "Import policy updated"

def show(connect, mtype=None, verbose=False, **kwargs):
    if mtype == None:
        raise FastScoreError("Model type not set (use -type: option)")
    engine = connect.lookup('engine')
    text = engine.policy.get('import', mtype)
    sys.stdout.write(text)
    sys.stdout.flush()

