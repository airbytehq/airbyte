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

# Input data: batch of four 28x28x3 images
input_shape = (4, 28, 28, 3)
x = tf.random.normal(input_shape)

# Convolution with 3x3 kernel, two output filters
y = tf.keras.layers.Conv2D(
    2,
    (3, 3),
    activation='relu',
    input_shape=input_shape[1:]
)(x)

assert y.shape == (4, 26, 26, 2), "Unexpected output shape!"
