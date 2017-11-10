
.PHONY: build clean

build:
	make -C sdk/python build
	python setup.py sdist

clean:
	make -sC sdk/python clean
	rm -rf dist *.egg-info

s3-push:
	aws s3 cp --acl public-read dist/fastscore-cli-dev.tar.gz s3://fastscore-cli/

