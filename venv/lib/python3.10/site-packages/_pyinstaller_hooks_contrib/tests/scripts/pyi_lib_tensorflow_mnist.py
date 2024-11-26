# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

import os

# Force CPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Display only warnings and errors
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Begin test - import tensorflow after environment variables are set
import tensorflow as tf  # noqa: E402

# Load and normalize the dataset
mnist = tf.keras.datasets.mnist

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

# Define model...
model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10)
])

# ... and loss function
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

# Train
model.compile(optimizer='adam', loss=loss_fn, metrics=['accuracy'])
model.fit(x_train, y_train, epochs=1, verbose=1)

# Evaluate
results = model.evaluate(x_test, y_test, verbose=1)

# Expected accuracy after a single epoch is around 95%, so use 90%
# as a passing bar
assert results[1] >= 0.90, "Resulting accuracy on validation set too low!"
