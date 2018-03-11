#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# File: tensorpack.alexnet.py
import tensorflow as tf
import numpy as np
from tensorpack import *

BATCH = 64

class Model(ModelDesc):
    def _get_inputs(self):
        return [InputDesc(tf.float32, [BATCH, 3, 224, 224], 'input'),
                InputDesc(tf.int32, [BATCH], 'label') ]

    def _build_graph(self, inputs):
        image, label = inputs
        image = image / 255.0

        with argscope(Conv2D, activation=tf.nn.relu, kernel_shape=3), \
                argscope([Conv2D, MaxPooling], data_format='NCHW'):
            logits = (LinearWrap(image)
                      .Conv2D('conv1_1', 64, kernel_shape=11, stride=4, padding='VALID')
                      .MaxPooling('pool1', 3, 2)
                      .Conv2D('conv1_2', 192, kernel_shape=5)
                      .MaxPooling('pool2', 3, 2)

                      .Conv2D('conv3', 384)
                      .Conv2D('conv4', 256)
                      .Conv2D('conv5', 256)
                      .MaxPooling('pool3', 3, 2)

                      .FullyConnected('fc6', 4096, activation=tf.nn.relu)
                      .Dropout('drop0', rate=0.5)
                      .FullyConnected('fc7', 4096, activation=tf.nn.relu)
                      .Dropout('drop1', rate=0.5)
                      .FullyConnected('fc8', out_dim=1000)())

        cost = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=label)
        self.cost = tf.reduce_mean(cost, name='cost')

    def _get_optimizer(self):
        return tf.train.RMSPropOptimizer(1e-3, epsilon=1e-8)


def get_data():
    X_train = np.random.random((BATCH, 3, 224, 224)).astype('float32')
    Y_train = np.random.random((BATCH,)).astype('int32')
    def gen():
        while True:
            yield [X_train, Y_train]
    return DataFromGenerator(gen)

if __name__ == '__main__':
    dataset_train = get_data()
    config = TrainConfig(
        model=Model(),
        data=QueueInput(dataset_train),
        callbacks=[],
        extra_callbacks=[ProgressBar(['cost'])],
        max_epoch=100,
        steps_per_epoch=200,
    )
    launch_train_with_config(config, SimpleTrainer())
