## How to build
Ensure docker is running, then:
```
$ git clone --recursive git@github.com:opendatagroup/fastscore-cli.git
$ cd fastscore-cli
$ make build
```

Find self-contained archive here: `dist/fastscore-cli-dev.tar.gz`

## How to install
```
tar xzf dist/fastscore-cli-dev.tar.gz
cd fastscore-cli-dev
python setup.py install
```
