FROM alpine

RUN apk add --no-cache py-setuptools ca-certificates

ADD dist/fastscore-cli-dev.tar.gz .
RUN cd fastscore-cli-dev && python setup.py install
CMD fastscore
