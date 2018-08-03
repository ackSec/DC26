# Snort in Docker
FROM ubuntu:14.04.4

MAINTAINER Jon Medina <jonmedinagmail.com>

RUN apt-get update && \
    apt-get install -y \
        python-setuptools \
        dnsutils \
        iputils-ping \
        git \
        nano \
        python-pip \
        python-dev \
        wget \
        build-essential \
        bison \
        flex \
        libpcap-dev \
        libpcre3-dev \
        libdumbnet-dev \
        zlib1g-dev \
        iptables-dev \
        libnetfilter-queue1 \
        tcpdump \
        unzip \
        vim && pip install --upgrade pip && pip install -U pip dpkt snortunsock

WORKDIR /opt

ENV DAQ_VERSION 2.0.6
RUN wget https://www.snort.org/downloads/snort/daq-${DAQ_VERSION}.tar.gz \
    && tar xvfz daq-${DAQ_VERSION}.tar.gz \
    && cd daq-${DAQ_VERSION} \
    && ./configure; make; make install

ENV SNORT_VERSION 2.9.8.2
RUN wget https://www.snort.org/downloads/snort/snort-${SNORT_VERSION}.tar.gz \
    && tar xvfz snort-${SNORT_VERSION}.tar.gz \
    && cd snort-${SNORT_VERSION} \
    && ./configure; make; make install

RUN ldconfig

RUN wget --no-check-certificate \
        https://github.com/John-Lin/snortunsock/archive/master.zip \
    && unzip master.zip


ADD mysnortrules /opt
RUN mkdir -p /var/log/snort && \
    mkdir -p /usr/local/lib/snort_dynamicrules && \
    mkdir -p /etc/snort && \
    cp -r /opt/rules /etc/snort/rules && \
    mkdir -p /etc/snort/preproc_rules && \
    mkdir -p /etc/snort/so_rules && \
    cp -r /opt/etc /etc/snort/etc && \
    touch /etc/snort/rules/white_list.rules /etc/snort/rules/black_list.rules

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    /opt/snort-${SNORT_VERSION}.tar.gz /opt/daq-${DAQ_VERSION}.tar.gz


ENV NETWORK_INTERFACE eth0

CMD ["snort", "-T", "-i", "echo ${NETWORK_INTERFACE}", "-c", "/etc/snort/etc/snort.conf"]
