FROM apache/airflow:1.10.12

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        telnet \
        vim \
        libmysqlclient-dev \
        procps \
        cron

WORKDIR /
RUN mkdir -p temp/service_account \
    && mkdir -p opt/airflow/service_account \
    && mkdir -p opt/airflow/www \
    && chown -R airflow:airflow temp \
    && chown -R airflow:airflow opt \
    && chown -R airflow:airflow opt/airflow/www

COPY entrypoint.sh /entrypoint-init
RUN chmod a+x /entrypoint-init

WORKDIR /opt/airflow

COPY --chown=airflow:airflow requirements.txt ./
RUN pip install -r requirements.txt

COPY ./dags ./dags

EXPOSE 8080 5555 8793

USER airflow

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/entrypoint-init"]