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

import pytest

from PyInstaller.utils.hooks import is_module_satisfies
from PyInstaller.utils.tests import importorskip


# Run the tests in onedir mode only
onedir_only = pytest.mark.parametrize('pyi_builder', ['onedir'], indirect=True)


# Basic import tests for sub-packages of skimage. Run only on demand, and only in onedir mode.
@pytest.mark.slow
@onedir_only
@importorskip('skimage')
@pytest.mark.skipif(
    not is_module_satisfies('scikit_image >= 0.16'),
    reason='The test supports only scikit-image >= 0.16.',
)
@pytest.mark.parametrize('submodule', [
    'color', 'data', 'draw', 'exposure', 'feature', 'filters', 'future',
    'graph', 'io', 'measure', 'metrics', 'morphology', 'registration',
    'restoration', 'segmentation', 'transform', 'util'
])
def test_skimage(pyi_builder, submodule):
    pyi_builder.test_source("""
        import skimage.{0}
        """.format(submodule))


# Test the ORB descriptor, which requires the data file with descriptor sample points.
@importorskip('skimage')
def test_skimage_feature_orb(pyi_builder):
    pyi_builder.test_source("""
        import skimage.feature
        import numpy as np

        # Prepare test images
        img1 = np.zeros((100, 100))
        img2 = np.zeros_like(img1)
        rng = np.random.default_rng(1984)
        square = rng.random((20, 20))
        img1[40:60, 40:60] = square
        img2[53:73, 53:73] = square

        # ORB detector/descriptor extractor
        detector_extractor1 = skimage.feature.ORB(n_keypoints=5)
        detector_extractor2 = skimage.feature.ORB(n_keypoints=5)

        # Process
        detector_extractor1.detect_and_extract(img1)
        detector_extractor2.detect_and_extract(img2)

        matches = skimage.feature.match_descriptors(
            detector_extractor1.descriptors,
            detector_extractor2.descriptors,
        )
        print(matches)
        """)
