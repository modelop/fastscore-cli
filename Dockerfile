FROM ubuntu

RUN apt-get update && apt-get -y install curl python-setuptools

ADD sdk/python/dist/fastscore-dev.tar.gz .
RUN cd fastscore-dev && python setup.py install

ADD dist/fastscore-cli-dev.tar.gz .
RUN cd fastscore-cli-dev && python setup.py install
CMD fastscore
