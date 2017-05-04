FROM ubuntu

RUN apt-get update && apt-get install -y \
    libpcap0.8 \
    libssl1.0.0 \
    libyaml-0-2 \
    python \
    python-pip

RUN mkdir -p /root/fastscore-cli/
WORKDIR /root/fastscore-cli/

COPY setup.py ./
COPY fastscore/ ./fastscore/
COPY extra/ ./extra/
COPY run.py ./

RUN python setup.py install
RUN mkdir -p /root/fastscore/
WORKDIR /root/fastscore/
CMD fastscore
    
