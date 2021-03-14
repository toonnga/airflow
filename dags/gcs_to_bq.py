from datetime import datetime, timedelta
from airflow.contrib.operators.postgres_to_gcs_operator import PostgresToGoogleCloudStorageOperator
from airflow import models
from airflow.operators import bash_operator
from airflow.models import DAG
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.gcs_download_operator import GoogleCloudStorageDownloadOperator
from airflow.contrib.operators.file_to_gcs import FileToGoogleCloudStorageOperator
import pandas as pd

def Tranform_Data():
        df = pd.read_json('user_log.json', lines=True)

        #rename column
        df.rename(columns={'action':'action', 'created_at':'created_at', 'id':'id', 'status':'success', 'updated_at':'updated_at', 'user_id':'user_id'}, inplace=True)

        #change datatype
        df['success'] = df['success'].astype(bool)
        df['created_at'] = df['created_at'].astype(str)
        df['updated_at'] = df['updated_at'].astype(str)

        print(df.to_string())

        df.to_json('/opt/airflow/user_log_transform.json', orient='records', lines=True)

args = {
        'owner': 'Kansinee K.',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        'start_date': datetime(2021, 3, 13),
    }

dag = DAG(dag_id='postgres_to_bq', default_args=args, schedule_interval=timedelta(hours=1), catchup=False)

postgres_to_gcs_users = PostgresToGoogleCloudStorageOperator(  
        task_id = 'postgres_to_gcs_users',
        sql = 'SELECT created_at, updated_at, id, first_name, last_name FROM users;',
        bucket = 'users-datalake',
        filename = 'users.json',
        approx_max_file_size_bytes=1900000000,
        postgres_conn_id = 'postgres_bluepi',
        google_cloud_storage_conn_id = 'gcs_datalake',
        delegate_to=None,
        parameters=None,
        dag=dag
    )

postgres_to_gcs_user_log = PostgresToGoogleCloudStorageOperator(  
        task_id = 'postgres_to_gcs_user_log',
        sql = 'SELECT created_at, updated_at, id, user_id, "action", status FROM public.user_log;',
        bucket = 'users-datalake',
        filename = 'user_log.json',
        approx_max_file_size_bytes=1900000000,
        postgres_conn_id = 'postgres_bluepi',
        google_cloud_storage_conn_id = 'gcs_datalake',
        delegate_to=None,
        parameters=None,
        dag=dag
    )

download_json_file = GoogleCloudStorageDownloadOperator(
        task_id='download_json_file',
        object='user_log.json',
        bucket='users-datalake',
        filename='/opt/airflow/user_log.json',
        google_cloud_storage_conn_id='gcs_datalake',
        dag=dag)

tranform_user_log = PythonOperator(
        task_id='tranform_user_log',
        python_callable=Tranform_Data,
        dag=dag)

tranform_to_gcs = FileToGoogleCloudStorageOperator(
        task_id='tranform_to_gcs',
        src='/opt/airflow/user_log_transform.json',
        dst='user_log_transform.json',
        bucket='users-datalake',
        google_cloud_storage_conn_id='gcs_datalake',
        dag=dag)

gcs_to_bq_users = GoogleCloudStorageToBigQueryOperator(
        task_id='gcs_to_bq_users',
        bucket='users-datalake',
        source_objects=['users.json'],
        schema_fields=[{"mode": "NULLABLE", "name": "created_at", "type": "TIMESTAMP"}, {"mode": "NULLABLE", "name": "updated_at", "type": "TIMESTAMP"}, {"mode": "NULLABLE", "name": "id", "type": "STRING"}, {"mode": "NULLABLE", "name": "first_name", "type": "STRING"}, {"mode": "NULLABLE", "name": "last_name", "type": "STRING"}],
        source_format='NEWLINE_DELIMITED_JSON',
        destination_project_dataset_table='de-exam-kansinee:data_warehouse.users',
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_TRUNCATE',
        bigquery_conn_id='bigquery_data_warehouse',
        google_cloud_storage_conn_id='gcs_datalake',
        dag=dag)

gcs_to_bq_user_log = GoogleCloudStorageToBigQueryOperator(
        task_id='gcs_to_bq_user_log',
        bucket='users-datalake',
        source_objects=['user_log_transform.json'],
        schema_fields=[{"mode": "NULLABLE", "name": "action", "type": "STRING"}, {"mode": "NULLABLE", "name": "created_at", "type": "TIMESTAMP"}, {"mode": "NULLABLE", "name": "id", "type": "STRING"}, {"mode": "NULLABLE", "name": "success", "type": "BOOLEAN"}, {"mode": "NULLABLE", "name": "updated_at", "type": "TIMESTAMP"}, {"mode": "NULLABLE", "name": "user_id", "type": "STRING"}],
        source_format='NEWLINE_DELIMITED_JSON',
        destination_project_dataset_table='de-exam-kansinee:data_warehouse.user_log',
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_TRUNCATE',
        bigquery_conn_id='bigquery_data_warehouse',
        google_cloud_storage_conn_id='gcs_datalake',
        dag=dag)

postgres_to_gcs_users >> gcs_to_bq_users
postgres_to_gcs_user_log >> download_json_file >> tranform_user_log >> tranform_to_gcs >> gcs_to_bq_user_log

