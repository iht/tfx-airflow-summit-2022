import tensorflow as tf
import tensorflow_transform as tft

from typing import Dict


def preprocessing_fn(inputs: Dict[str, tf.Tensor]) -> Dict[str, tf.Tensor]:
    cols_to_normalize = ['petal_length', 'petal_width', 'sepal_length', 'sepal_width']
    output_dict = {}

    for col in cols_to_normalize:
        output_dict[col] = tft.scale_to_0_1(inputs[col])

    return output_dict
