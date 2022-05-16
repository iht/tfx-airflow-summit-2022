from datetime import datetime

import tfx.v1 as tfx
from tfx.extensions.google_cloud_big_query.example_gen.component import BigQueryExampleGen
from tfx.orchestration.airflow.airflow_dag_runner import AirflowDagRunner


def create_pipeline(query: str,
                    pipeline_name: str,
                    pipeline_root: str) -> tfx.dsl.Pipeline:
    example_gen: BigQueryExampleGen = tfx.extensions.google_cloud_big_query.BigQueryExampleGen(query=query)

    components = [example_gen]

    pipeline = tfx.dsl.Pipeline(pipeline_name="",
                                pipeline_root="",
                                components=components,
                                enable_cache=True)

    return pipeline


def main(query: str,
         pipeline_name: str,
         pipeline_root: str):
    p: tfx.dsl.Pipeline = create_pipeline(query=query,
                                          pipeline_name=pipeline_name,
                                          pipeline_root=pipeline_root)

    airflow_config = {
        'schedule_interval': None,
        'start_date': datetime(2022, 1, 1),
    }

    runner = AirflowDagRunner(airflow_config)

    return runner.run(p)


PIPELINE_NAME = "01-tfx-airflow-summit-2022"
PIPELINE_ROOT = "/tmp/tfx-airflow-summit-2022"

QUERY = "SELECT * FROM `bigquery-public-data.austin_311.311_service_requests` LIMIT 1000"

DAG = main(query=QUERY,
           pipeline_name=PIPELINE_NAME,
           pipeline_root=PIPELINE_ROOT)
