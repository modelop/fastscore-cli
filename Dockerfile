FROM alpine:3.6

RUN apk add --no-cache python && \
    python -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip install --upgrade pip setuptools && \
    rm -r /root/.cache

RUN echo "@testing http://nl.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories \
    && apk --update add \
    bash \
    git \
    curl \
    ca-certificates \
    bzip2 \
    unzip \
    sudo \
    libstdc++ \
    glib \
    libxext \
    libxrender \
    tini@testing \
    && curl "https://raw.githubusercontent.com/sgerrand/alpine-pkg-glibc/master/sgerrand.rsa.pub" -o /etc/apk/keys/sgerrand.rsa.pub \
    && curl -L "https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.23-r3/glibc-2.23-r3.apk" -o glibc.apk \
    && apk add glibc.apk \
    && curl -L "https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.23-r3/glibc-bin-2.23-r3.apk" -o glibc-bin.apk \
    && apk add glibc-bin.apk \
    && /usr/glibc-compat/sbin/ldconfig /lib /usr/glibc/usr/lib \
    && rm -rf glibc*apk /var/cache/apk/*

# Configure environment
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH
ENV SHELL /bin/bash
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Configure Miniconda
ENV MINICONDA_VER 4.2.12
ENV MINICONDA Miniconda2-$MINICONDA_VER-Linux-x86_64.sh
ENV MINICONDA_URL https://repo.continuum.io/miniconda/$MINICONDA
ENV MINICONDA_MD5_SUM d0c7c71cc5659e54ab51f2005a8d96f3

RUN mkdir -p $CONDA_DIR
RUN cd /tmp && \
    curl -L $MINICONDA_URL -o miniconda.sh && \
    /bin/bash miniconda.sh -f -b -p $CONDA_DIR && \
    rm miniconda.sh && \
    $CONDA_DIR/bin/conda install --yes conda==$MINICONDA_VER

RUN conda install pandas

# RUN curl -L https://s3-us-west-1.amazonaws.com/fastscore-cli/fastscore-cli-1.5.tar.gz | tar xz
# RUN cd fastscore-cli-1.5 && python setup.py install

ADD dist/fastscore-cli-dev.tar.gz .
RUN cd fastscore-cli-dev && python setup.py install
CMD fastscore
