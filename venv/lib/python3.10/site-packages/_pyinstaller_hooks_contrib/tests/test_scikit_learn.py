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


# Basic import tests for sub-packages of sklearn.  Run only on demand, and only in onedir mode.
@pytest.mark.slow
@onedir_only
@importorskip('sklearn')
@pytest.mark.skipif(
    not is_module_satisfies('scikit_learn >= 0.21'),
    reason='The test supports only scikit-learn >= 0.21.',
)
@pytest.mark.parametrize('submodule', [
    'calibration', 'cluster', 'covariance', 'cross_decomposition',
    'datasets', 'decomposition', 'dummy', 'ensemble', 'exceptions',
    'experimental', 'externals', 'feature_extraction',
    'feature_selection', 'gaussian_process', 'inspection',
    'isotonic', 'kernel_approximation', 'kernel_ridge',
    'linear_model', 'manifold', 'metrics', 'mixture',
    'model_selection', 'multiclass', 'multioutput',
    'naive_bayes', 'neighbors', 'neural_network', 'pipeline',
    'preprocessing', 'random_projection', 'semi_supervised',
    'svm', 'tree', 'discriminant_analysis', 'impute', 'compose'
])
def test_sklearn(pyi_builder, submodule):
    pyi_builder.test_source("""
        import sklearn.{0}
        """.format(submodule))
