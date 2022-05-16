from typing import Dict, List

import tensorflow as tf
import tensorflow_transform as tft
import tfx.v1 as tfx
from tfx_bsl.public import tfxio

import logging

from tensorflow_metadata.proto.v0.schema_pb2 import Schema
from tensorflow_transform import TFTransformOutput
from tfx.components.trainer.fn_args_utils import FnArgs

from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras import layers
from tensorflow.keras import activations
from tensorflow.keras import optimizers
from tensorflow.keras import losses
from tensorflow.keras import metrics


def parse_data(location: List[str],
               data_accessor: tfx.components.DataAccessor,
               schema: Schema) -> tf.data.Dataset:
    return data_accessor.tf_dataset_factory(
        location,
        tfxio.TensorFlowDatasetOptions(batch_size=1024, label_key="species"),
        schema=schema).repeat()


def build_model(feature_names: List[str]) -> models.Model:
    input_layers = [layers.Input(shape=(1,), name=f) for f in feature_names]
    c = layers.concatenate(input_layers)
    c = layers.Dense(256, activation=activations.relu)(c)
    outputs = layers.Dense(1, activation=activations.sigmoid)(c)
    model = models.Model(inputs=input_layers, outputs=outputs)

    model.compile(
        optimizer=optimizers.RMSprop(),
        loss=losses.binary_crossentropy,
        metrics=[metrics.binary_accuracy])

    model.summary(print_fn=logging.info)

    return model


def get_feature_cols(d: Dict) -> List[str]:
    features = [k for k in d.keys() if k.startswith("petal") or k.startswith("sepal")]
    return features


def run_fn(fn_args: FnArgs):
    tft_output_path = fn_args.transform_graph_path
    tft_output: TFTransformOutput = tft.TFTransformOutput(tft_output_path)
    schema: Schema = tft_output.transformed_metadata.schema
    col_names: Dict = tft_output.transformed_feature_spec()
    feature_names = get_feature_cols(col_names)

    data_accessor = fn_args.data_accessor

    train_files: List[str] = fn_args.train_files
    train_ds: tf.data.Dataset = parse_data(train_files, data_accessor, schema)
    eval_files = fn_args.eval_files
    eval_ds: tf.data.Dataset = parse_data(eval_files, data_accessor, schema)

    m = build_model(feature_names)
    m.fit(train_ds,
          epochs=fn_args.train_steps,
          steps_per_epoch=1,
          validation_data=eval_ds,
          validation_steps=1)

    m.save(fn_args.serving_model_dir)
