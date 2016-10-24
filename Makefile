
.PHONY: default

default:
	python setup.py sdist
	aws s3 cp --acl public-read dist/fastscore-cli-dev.tar.gz s3://fastscore-cli/

