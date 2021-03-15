airflow
====

Airflow project for creating DAG for ETL process 

## Loading datalake(GCS) to data warehouse(Bigquery)

There are 3 main components pipeline: postgres > gcs, tranform_data, gcs > bigquery

postgres > gcs: load data from postgres database to gcs
tranform_data: load data from gcs to local > tranform data and put json file into cluster > push file from cluster to gcs
gcs > bigquery: load data from gcs to bigquery


### Postgres to GCS

load data from postgres database to gcs

task: 
    - postgres_to_gcs_users
    - postgres_to_gcs_user_log

Example for create task:

```python
postgres_to_gcs_users = PostgresToGoogleCloudStorageOperator(  
        task_id = '{task_id}',
        sql = '{sql command}',
        bucket = '{bucket name}',
        filename = '{filename.json}',
        approx_max_file_size_bytes={file size in bytes},
        postgres_conn_id = '{postgres conn id}',
        google_cloud_storage_conn_id = '{gcs conn id}',
        delegate_to=None,
        parameters=None,
        dag=dag
    )
```

### Tranform Data

-   load data from gcs to local
    
    task: 
    - download_json_file

    Example for create task:

    ```python
    download_json_file = GoogleCloudStorageDownloadOperator(
        task_id='{task_id}',
        object='{source json file}',
        bucket='{source bucket name}',
        filename='{path/to/local/json/file}',
        google_cloud_storage_conn_id='{gcs conn id}',
        dag=dag)
        )
    ```

-   tranform data and put json file into cluster

    task: 
    - tranform_user_log - call function Tranform_Data() for rename column, change datatype and push json file to cluster

    Example for create task:

    ```python
    tranform_user_log = PythonOperator(
        task_id='{task_id}',
        python_callable=Tranform_Data,
        dag=dag)
    ```

-   push file from cluster to gcs

    task: 
    - tranform_to_gcs

    Example for create task:

    ```python
    tranform_to_gcs = FileToGoogleCloudStorageOperator(
        task_id='{task_id}',
        src='{path/to/json/file/in/cluster}',
        dst='{json_file_name_to_gcs.json}',
        bucket='{target bucket name}',
        google_cloud_storage_conn_id='{gcs conn id}',
        dag=dag)
    ```

### GCS > Bigquery

load data from gcs to bigquery

task: 
    - gcs_to_bq_users
    - gcs_to_bq_user_log

Example for create task:

```python
gcs_to_bq_users = GoogleCloudStorageToBigQueryOperator(
        task_id='{task_id}',
        bucket='{source bucket name}',
        source_objects=['{json file name}'],
        schema_fields={schema fields},
        source_format='NEWLINE_DELIMITED_JSON',
        destination_project_dataset_table='{project_id:dataset.table}',
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_TRUNCATE',
        bigquery_conn_id='{bigquery conn id}',
        google_cloud_storage_conn_id='{gcs conn id}',
        dag=dag)
```

## Build airflow image and push image to gcr

```bash
chmod +x push_gcr.sh
./push_gcr.sh
```

## Running software stack using docker-compose

### Run local

    1. run ./secret_data_pull.sh
    2. docker-compose up

### Stop local

    ```bash
    docker-compose down
    ```

### Note

** If change/add/remove any service-account folder or airflow.cfg please always run `./secret_data_push.sh`


## Other Script Description

- airflow.cfg: airflow config
- create-connection.sh: scripts for create connection after airflow start
- docker-compose.yaml: for run airflow docker in local (docker-compose up/down)
- Dockerfile: for build airflow image
- entrypoint.sh: decorate entrypoint for airflow image
- push_gcr.sh: script for build and push airflow image to GCR
- secret_data_pull.sh: script for pull service-account, airflow.cfg (sensitive data) to GCS
- secret_data_push.sh: script for push service-account, airflow.cfg (sensitive data) to GCS
