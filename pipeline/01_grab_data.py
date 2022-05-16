import os

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
                    beam_args: List[str],
                    transform_file_location: str) -> tfx.dsl.Pipeline:
    # Grab data
    example_gen: BigQueryExampleGen = tfx.extensions.google_cloud_big_query.BigQueryExampleGen(query=query)

    # Generate statistics
    stats_gen = tfx.components.StatisticsGen(examples=example_gen.outputs['examples'])

    schema_gen = tfx.components.SchemaGen(statistics=stats_gen.outputs["statistics"])

    validator = tfx.components.ExampleValidator(statistics=stats_gen.outputs['statistics'],
                                                schema=schema_gen.outputs["schema"])

    # Feature engineering
    transform = tfx.components.Transform(examples=example_gen.outputs['examples'],
                                         schema=schema_gen.outputs['schema'],
                                         module_file=transform_file_location)

    components = [example_gen, stats_gen, schema_gen, validator, transform]

    metadata_conn = metadata.sqlite_metadata_connection_config(metadata_path)

    pipeline = tfx.dsl.Pipeline(pipeline_name=pipeline_name,
                                pipeline_root=pipeline_root,
                                components=components,
                                metadata_connection_config=metadata_conn,
                                beam_pipeline_args=beam_args,
                                enable_cache=False)

    return pipeline


def main(query: str,
         pipeline_name: str,
         pipeline_root: str,
         metadata_path: str,
         beam_args: List[str],
         transform_file_location: str):
    p: tfx.dsl.Pipeline = create_pipeline(query=query,
                                          pipeline_name=pipeline_name,
                                          pipeline_root=pipeline_root,
                                          metadata_path=metadata_path,
                                          beam_args=beam_args,
                                          transform_file_location=transform_file_location)

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

BEAM_ARGS_LOCAL = ["--runner=DirectRunner", f"--temp_location={GCS_TEMP_PATH}", f"--project={GCP_PROJECT}"]
TRANSFORM_FILE_LOCATION_LOCAL = "/Users/ihr/projects/airflow-summit-2022/pipeline/preprocessing_fn.py"

BEAM_ARGS_CLOUD = ["--runner=DataflowRunner",
                   f"--temp_location={GCS_TEMP_PATH}",
                   f"--project={GCP_PROJECT}",
                   "--region=europe-west3",
                   "--service_account_email=tfx-sa@tfx-airflow-summit-2022.iam.gserviceaccount.com",
                   "--subnetwork=regions/europe-west3/subnetworks/default",
                   "--no_use_public_ips"]
TRANSFORM_FILE_LOCATION_CLOUD = "gs://tfx-airflow-summit-2022/transforms/preprocessing_fn.py"

DAG = main(query=QUERY,
           pipeline_name=PIPELINE_NAME,
           pipeline_root=PIPELINE_ROOT,
           metadata_path=METADATA_PATH,
           beam_args=BEAM_ARGS_CLOUD,
           transform_file_location=TRANSFORM_FILE_LOCATION_CLOUD)
