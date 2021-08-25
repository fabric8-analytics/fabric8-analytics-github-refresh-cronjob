FROM registry.access.redhat.com/ubi8/python-36:latest

RUN yum install -y epel-release &&\
    yum install -y git python36-pip python36-devel &&\
    yum clean all

ENV APP_DIR=/github_refresh

RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}

COPY . ${APP_DIR}
RUN python3 -m pip install --upgrade pip>=10.0.0 && pip3 install -r requirements.txt

CMD ["python3", "-u", "./src/github_refresh.py"]
