FROM registry.centos.org/centos/centos:7

RUN yum install -y epel-release &&\
    yum install -y git python36-pip python36-devel &&\
    yum clean all

ENV APP_DIR=/github_refresh

RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}

COPY . ${APP_DIR}
RUN pip3 install --upgrade pip>=10.0.0 && pip3 install -r requirements.txt

CMD ["python3", "-u", "./github_refresh.py"]
