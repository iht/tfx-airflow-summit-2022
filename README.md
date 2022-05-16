# tfx-airflow-summit-2022

Python 3.7

Install Mariadb `brew install mariadb`

`airflow db init`

Create a user `airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin`

`airflow webserver -p 8080`

Change `expose_config = True` in ~/airflow/airflow.cfg

Run `airflow scheduler` in another terminal

Run Bigquery without setting any beam options, check it fails, check BQ jobs 
in console UI https://console.cloud.google.com/bigquery?project=tfx-airflow-summit-2022

Add beam pipeline args for the direct runner

Check output in /tmp
find /tmp/tfx-airflow-summit-2022/BigQueryExampleGen/examples/

Add statistics, schema and validator