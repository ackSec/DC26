# Set the base image
FROM ubuntu
# Dockerfile author / maintainer
MAINTAINER Name <email.id@here>

RUN apt && apt upgrade -y
RUN git clone https://github.com/smythtech/sdnpwn.git
RUN chmod +x sdnpwn/sdnpwn.py && sudo chmod +x sdnpwn/setup.sh
RUN ./setup.sh
