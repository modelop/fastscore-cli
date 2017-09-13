FROM ubuntu

RUN apt-get update && apt-get -y install curl python-setuptools python-dev g++
RUN easy_install pandas

RUN curl -L https://s3-us-west-1.amazonaws.com/fastscore-cli/fastscore-cli-1.5.tar.gz | tar xz
RUN cd fastscore-cli-1.5 && python setup.py install

ADD dist/fastscore-cli-dev.tar.gz .
RUN cd fastscore-cli-dev && python setup.py install
CMD fastscore
