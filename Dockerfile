FROM alpine

RUN apk add --no-cache make py2-pip python3 &&\
	pip2 install --upgrade pip &&\
	pip3 install --upgrade pip &&\
	pip2 install wheel &&\
	pip3 install wheel

WORKDIR /_

COPY Makefile .
COPY setup.py .
COPY MANIFEST.in .
COPY fastscore fastscore
COPY extra extra
COPY cli cli

RUN make dist
