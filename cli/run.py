
import cli.model, cli.stream

from .colors import tcol

from fastscore.pneumo import EngineStateMsg, ModelErrorMsg

from fastscore import FastScoreError

def run(connect, model_name, stream_name0, stream_name1,
            verbose=False, embedded_schemas={}, wait=False, **kwargs):
    cli.model.verify(connect, model_name, quiet=True, embedded_schemas=embedded_schemas, **kwargs)
    cli.stream.verify(connect, stream_name0, 0, quiet=True, **kwargs)
    cli.stream.verify(connect, stream_name0, 1, quiet=True, **kwargs)

    if verbose:
        print tcol.OKGREEN + "Model and streams verified successfully" + tcol.ENDC

    cli.model.load(connect, model_name, verbose=verbose, embedded_schemas=embedded_schemas, **kwargs)
    cli.stream.attach(connect, stream_name0, 0, verbose=verbose, **kwargs)
    cli.stream.attach(connect, stream_name1, 1, verbose=verbose, **kwargs)

    if wait:
        pneumo = connect.pneumo.socket()
        while True:
            msg = pneumo.recv()
            if isinstance(msg, EngineStateMsg):
                if verbose:
                    print "Engine state is " + msg.state.upper()
                if msg.state == "finished":
                    break
            elif isinstance(msg, ModelErrorMsg):
                print tcol.FAIL + str(msg) + tcol.ENDC
                break

        pneumo.close()

