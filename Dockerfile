FROM ubuntu

RUN apt-get update && apt-get -y install curl python-pip

# FIXME: without fastscore-sdk installed CLI refuses to install
ADD sdk /sdk
RUN cd /sdk/python && python setup.py install

ADD dist/fastscore-cli-dev.tar.gz .
RUN cd fastscore-cli-dev && python setup.py install
CMD fastscore
