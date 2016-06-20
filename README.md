
# fastscore-cli

This is an early prototype of the FastScore CLI.

The next version should use virtualenv to capture dependencies of the utility.

# How to use

The tool must know the Connect endpoint. To set the endpoint:
```
fastscore connect https://127.0.0.1:8001
```

This saves the endpoint into a file named `.fastscore` in the current directory.

The next mandatory command is to set the Connect configuration.
```
fastscore config set config.yaml
```

Run `fastscore` or `fastscore help` to get the list of commands.

