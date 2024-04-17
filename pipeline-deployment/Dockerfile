FROM quay.io/astronomer/astro-runtime:11.0.0
ENV AIRFLOW_DAGBAG_IMPORT_TIMEOUT=600000
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY requirements.txt /requirements.txt
COPY .astro /.astro
USER root
RUN mkdir /opt/airflow

COPY src /opt/airflow/src
RUN chmod -R 777 /opt/airflow/
RUN apt-get update && apt-get install -y git
ENV HOME=/opt/airflow
USER astro
RUN pip install cloudscraper
RUN pip install -r /requirements.txt
USER root
RUN mkdir /opt/airflow/myrepo
WORKDIR /opt/airflow/myrepo
RUN chmod -R 777 /opt/airflow/myrepo

RUN git clone --depth 1 https://github.com/HazemEldabaa/immo-eliza-deployment.git .


WORKDIR /

RUN git config --global user.email "eldabaahazem@gmail.com" && \
    git config --global user.name "HazemEldabaa" && \
    git config --global --add safe.directory /opt/airflow/myrepo

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

