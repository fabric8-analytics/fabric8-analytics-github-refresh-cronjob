FROM registry.centos.org/centos/centos:7

RUN yum install -y epel-release &&\
    yum install -y git python34-pip python34-devel &&\
    yum clean all

ENV APP_DIR=/github_refresh

RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}

COPY . ${APP_DIR}
RUN pip3 install -r requirements.txt

CMD ["python3", "./github_refresh.py"]
