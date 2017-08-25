
OBSOLETE - NEEDS A REVIEW

# FastScore CLI

This is the command line interface (CLI) to FastScore.

## How to install
```
wget https://s3-us-west-1.amazonaws.com/fastscore-cli/fastscore-cli-1.5.tar.gz
tar xzf fastscore-cli-1.5.tar.gz
cd fastscore-cli-1.5
python setup.py install
```

To verify the installation run:
```
fastscore help
```

## How to use

The tool must know the Connect endpoint. To set the endpoint run:
```
fastscore connect https://127.0.0.1:8001
```

This saves the endpoint into a file named `.fastscore` in the current directory.

The next mandatory step is to set the Connect configuration.
```
fastscore config set config.yaml
```

Run `fastscore help` to get the list of commands.

Run `fastscore` without parameters to enter an interactive mode. In interactive
mode you will receive asynchronous notifications from FastScore.

