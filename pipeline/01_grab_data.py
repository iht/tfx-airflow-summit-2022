from datetime import datetime
from typing import List

import tfx.v1 as tfx
from tfx.extensions.google_cloud_big_query.example_gen.component import BigQueryExampleGen
from tfx.orchestration import metadata
from tfx.orchestration.airflow.airflow_dag_runner import AirflowDagRunner


def create_pipeline(query: str,
                    pipeline_name: str,
                    pipeline_root: str,
                    metadata_path: str,
                    beam_args: List[str]) -> tfx.dsl.Pipeline:
    example_gen: BigQueryExampleGen = tfx.extensions.google_cloud_big_query.BigQueryExampleGen(query=query)

    stats_gen = tfx.components.StatisticsGen(examples=example_gen.outputs['examples'])

    schema_gen = tfx.components.SchemaGen(statistics=stats_gen.outputs["statistics"])

    validator = tfx.components.ExampleValidator(statistics=stats_gen.outputs['statistics'],
                                                schema=schema_gen.outputs["schema"])

    components = [example_gen, stats_gen, schema_gen, validator]

    metadata_conn = metadata.sqlite_metadata_connection_config(metadata_path)

    pipeline = tfx.dsl.Pipeline(pipeline_name=pipeline_name,
                                pipeline_root=pipeline_root,
                                components=components,
                                metadata_connection_config=metadata_conn,
                                beam_pipeline_args=beam_args,
                                enable_cache=True)

    return pipeline


def main(query: str,
         pipeline_name: str,
         pipeline_root: str,
         metadata_path: str,
         beam_args: List[str]):
    p: tfx.dsl.Pipeline = create_pipeline(query=query,
                                          pipeline_name=pipeline_name,
                                          pipeline_root=pipeline_root,
                                          metadata_path=metadata_path,
                                          beam_args=beam_args)

    airflow_config = {
        'schedule_interval': None,
        'start_date': datetime(2022, 1, 1),
    }

    runner = AirflowDagRunner(config=airflow_config)

    return runner.run(p)


PIPELINE_NAME = "01_tfx_airflow_summit"
PIPELINE_ROOT = "/tmp/tfx-airflow-summit-2022"
METADATA_PATH = "/tmp/tfx/metadata.db"

QUERY = "SELECT * FROM `bigquery-public-data.ml_datasets.iris`"

GCS_TEMP_PATH = "gs://tfx-airflow-summit-2022/tmp"
GCP_PROJECT = "tfx-airflow-summit-2022"

BEAM_ARGS = ["--runner=DirectRunner", f"--temp_location={GCS_TEMP_PATH}", f"--project={GCP_PROJECT}"]

DAG = main(query=QUERY,
           pipeline_name=PIPELINE_NAME,
           pipeline_root=PIPELINE_ROOT,
           metadata_path=METADATA_PATH,
           beam_args=BEAM_ARGS)
