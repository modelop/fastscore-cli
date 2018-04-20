build: sdk
	docker build --rm -t fastscore/cli-build .
	ID=`docker create fastscore/cli-build` && docker cp $$ID:/_/dist . && docker rm $$ID

dist:
	rm -rf build && python2 setup.py sdist
	rm -rf build && python2 setup.py bdist_wheel
	rm -rf build && python3 setup.py bdist_wheel

sdk:
	docker build --force-rm -t fastscore/sdk-build sdk
	ID=`docker create fastscore/sdk-build` && docker cp $$ID:/_/python/fastscore . && docker rm $$ID

clean:
	rm -rf dist build *.egg-info fastscore

s3-push:
	aws s3 cp --acl public-read dist/fastscore-cli-dev.tar.gz s3://fastscore-cli/

.PHONY: build dist sdk clean s3-push
