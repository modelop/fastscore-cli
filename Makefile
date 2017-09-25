
.PHONY: build clean

build:
	make -C sdk/python build
	python setup.py sdist

clean:
	make -sC sdk/python clean
	rm -rf dist *.egg-info
