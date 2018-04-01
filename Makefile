
.PHONY: build wheel sdk clean s3-push

build: sdk
	python setup.py sdist

wheel: sdk
	rm -rf build *.egg-info
	python2 setup.py bdist_wheel
	rm -rf build *.egg-info
	python3 setup.py bdist_wheel

sdk:
	make -C sdk/python build

clean:
	make -sC sdk/python clean
	rm -rf dist build *.egg-info

s3-push:
	aws s3 cp --acl public-read dist/fastscore-cli-dev.tar.gz s3://fastscore-cli/
