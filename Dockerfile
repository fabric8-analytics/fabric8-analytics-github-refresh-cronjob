FROM registry.access.redhat.com/ubi8/ubi-minimal:latest

RUN microdnf update -y && rm -rf /var/cache/yum
RUN microdnf install python3 git && microdnf clean all
RUN microdnf install which  
RUN pip3 install --upgrade pip --no-cache-dir


ENV APP_DIR=/github_refresh

RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}

COPY . ${APP_DIR}
RUN python3 -m pip install --upgrade pip>=10.0.0 && pip3 install -r requirements.txt

CMD ["./qa/runtests.sh"]