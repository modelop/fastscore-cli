
.PHONY: default build compile clean

default:
	@echo "BUILD_DATE = \"`date`\"" > fastscore/version.py
	python setup.py sdist
	#aws s3 cp --acl public-read dist/fastscore-cli-dev.tar.gz s3://fastscore-cli/

build:
	docker build -f Dockerfile.build --force-rm --build-arg uid=`id -u` --build-arg gid=`id -g` -t fastscore/cli-build .
	docker run --rm -v $(CURDIR):/_ fastscore/cli-build make compile
	docker build --force-rm -t fastscore/cli .

compile:
	make -C sdk/python v1-api v2-api
	python setup.py sdist

clean:
	echo TODO
