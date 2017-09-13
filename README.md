## How to build
Ensure docker is running, then:
```
$ git clone --recursive git@github.com:opendatagroup/fastscore-cli.git
$ cd fastscore-cli
$ make build
```

This will create:
* Package file `dist/fastscore-cli-dev.tar.gz`
* docker image `fastscore/cli-build` used to build this package
* docker image `fastscore/cli` with package installed
