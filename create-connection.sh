#!/usr/bin/env bash

## clear connection before add new connection

airflow connections -d --conn_id gcr_puller
airflow connections -d --conn_id gcs_datalake
airflow connections -d --conn_id postgres_bluepi
airflow connections -d --conn_id bigquery_data_warehouse

## add docker connection
airflow connections --add --conn_id=gcr_puller --conn_type=docker --conn_host='us.gcr.io/de-exam-kansinee' --conn_login='_json_key' --conn_password='$(cat /opt/airflow/service_account/de-exam-kansinee-gcr-puller.json)'

## add gcs datalake connection
airflow connections --add --conn_id=gcs_datalake --conn_type=google_cloud_platform --conn_extra='{ "extra__google_cloud_platform__key_path":"/opt/airflow/service_account/de-exam-kansinee-airflow.json", "extra__google_cloud_platform__project": "de-exam-kansinee" }'

export GOOGLE_APPLICATION_CREDENTIALS='/opt/airflow/service_account/de-exam-kansinee-airflow.json'

##source postgres
airflow connections --add --conn_id=postgres_bluepi --conn_uri='postgres://exam:bluePiExam@35.247.174.171:5432/postgres'

##data_warehouse bigquery connection

airflow connections --add --conn_id=bigquery_data_warehouse --conn_type=google_cloud_platform --conn_extra='{ "extra__google_cloud_platform__key_path":"/opt/airflow/service_account/de-exam-kansinee-airflow.json", "extra__google_cloud_platform__project": "de-exam-kansinee" }'
