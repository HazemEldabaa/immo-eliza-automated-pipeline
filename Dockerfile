FROM apache/airflow:latest
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt
USER root

RUN apt-get update && apt-get install -y git
USER airflow
RUN mkdir -p /opt/airflow/myrepo

WORKDIR /opt/airflow/myrepo
RUN git clone --depth 1 https://github.com/HazemEldabaa/immo-eliza-deployment.git .


RUN git config --global user.email "eldabaahazem@gmail.com" && \
    git config --global user.name "HazemEldabaa"

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

