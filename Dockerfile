FROM registry.access.redhat.com/ubi8/python-36:latest

ENV APP_DIR=/github_refresh

USER root
RUN mkdir -p ${APP_DIR}
RUN chown root ${APP_DIR}
# USER mbharatk
WORKDIR ${APP_DIR}

ADD ./requirements.txt .
RUN python3 -m pip install --upgrade pip>=10.0.0 && pip3 install -r requirements.txt

CMD ["python3", "-u", "./src/github_refresh.py"]
