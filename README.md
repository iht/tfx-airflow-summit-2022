# tfx-airflow-summit-2022

Python 3.7

Install Mariadb `brew install mariadb`

`airflow db init`

Create a user `airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin`

`airflow webserver -p 8080`

Change `expose_config = True` in ~/airflow/airflow.cfg

Run `airflow scheduler` in another terminal