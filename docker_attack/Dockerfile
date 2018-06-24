# Set the base image
FROM ubuntu
# Dockerfile author / maintainer
MAINTAINER ackSec

RUN cd ~
RUN apt update && apt upgrade -y && apt-get install -y git
RUN git clone https://github.com/ackSec/sdnpwn.git
RUN chmod +x sdnpwn/sdnpwn.py && chmod +x sdnpwn/setup.sh
RUN sdnpwn/setup.sh
RUN cd ~
