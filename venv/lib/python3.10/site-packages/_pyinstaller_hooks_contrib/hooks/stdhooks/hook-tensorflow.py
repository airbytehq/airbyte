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

from _pyinstaller_hooks_contrib.compat import importlib_metadata
from packaging.version import Version

from PyInstaller.compat import is_linux
from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
    get_module_attribute,
    is_module_satisfies,
    logger,
)

# Determine the name of `tensorflow` dist; this is available under different names (releases vs. nightly, plus build
# variants). We need to determine the dist that we are dealing with, so we can query its version and metadata.
_CANDIDATE_DIST_NAMES = (
    "tensorflow",
    "tensorflow-cpu",
    "tensorflow-gpu",
    "tensorflow-intel",
    "tensorflow-rocm",
    "tensorflow-macos",
    "tensorflow-aarch64",
    "tensorflow-cpu-aws",
    "tf-nightly",
    "tf-nightly-cpu",
    "tf-nightly-gpu",
    "tf-nightly-rocm",
    "intel-tensorflow",
    "intel-tensorflow-avx512",
)
dist = None
for candidate_dist_name in _CANDIDATE_DIST_NAMES:
    try:
        dist = importlib_metadata.distribution(candidate_dist_name)
        break
    except importlib_metadata.PackageNotFoundError:
        continue

version = None
if dist is None:
    logger.warning(
        "hook-tensorflow: failed to determine tensorflow dist name! Reading version from tensorflow.__version__!"
    )
    try:
        version = get_module_attribute("tensorflow", "__version__")
    except Exception as e:
        raise Exception("Failed to read tensorflow.__version__") from e
else:
    logger.info("hook-tensorflow: tensorflow dist name: %s", dist.name)
    version = dist.version

# Parse version
logger.info("hook-tensorflow: tensorflow version: %s", version)
try:
    version = Version(version)
except Exception as e:
    raise Exception("Failed to parse tensorflow version!") from e

# Exclude from data collection:
#  - development headers in include subdirectory
#  - XLA AOT runtime sources
#  - libtensorflow_framework and libtensorflow_cc (since TF 2.12) shared libraries (to avoid duplication)
#  - import library (.lib) files (Windows-only)
data_excludes = [
    "include",
    "xla_aot_runtime_src",
    "libtensorflow_framework.*",
    "libtensorflow_cc.*",
    "**/*.lib",
]

# Under tensorflow 2.3.0 (the most recent version at the time of writing), _pywrap_tensorflow_internal extension module
# ends up duplicated; once as an extension, and once as a shared library. In addition to increasing program size, this
# also causes problems on macOS, so we try to prevent the extension module "variant" from being picked up.
#
# See pyinstaller/pyinstaller-hooks-contrib#49 for details.
#
# With PyInstaller >= 6.0, this issue is alleviated, because the binary dependency analysis (which picks up the
# extension in question as a shared library that other extensions are linked against) now preserves the parent directory
# layout, and creates a symbolic link to the top-level application directory.
if is_module_satisfies('PyInstaller >= 6.0'):
    excluded_submodules = []
else:
    excluded_submodules = ['tensorflow.python._pywrap_tensorflow_internal']


def _submodules_filter(x):
    return x not in excluded_submodules


if version < Version("1.15.0a0"):
    # 1.14.x and earlier: collect everything from tensorflow
    hiddenimports = collect_submodules('tensorflow', filter=_submodules_filter)
    datas = collect_data_files('tensorflow', excludes=data_excludes)
elif version >= Version("1.15.0a0") and version < Version("2.2.0a0"):
    # 1.15.x - 2.1.x: collect everything from tensorflow_core
    hiddenimports = collect_submodules('tensorflow_core', filter=_submodules_filter)
    datas = collect_data_files('tensorflow_core', excludes=data_excludes)

    # Under 1.15.x, we seem to fail collecting a specific submodule, and need to add it manually...
    if version < Version("2.0.0a0"):
        hiddenimports += ['tensorflow_core._api.v1.compat.v2.summary.experimental']
else:
    # 2.2.0 and newer: collect everything from tensorflow again
    hiddenimports = collect_submodules('tensorflow', filter=_submodules_filter)
    datas = collect_data_files('tensorflow', excludes=data_excludes)

    # From 2.6.0 on, we also need to explicitly collect keras (due to lazy mapping of tensorflow.keras.xyz -> keras.xyz)
    if version >= Version("2.6.0a0"):
        hiddenimports += collect_submodules('keras')

    # Starting with 2.14.0, we need `ml_dtypes` among hidden imports.
    if version >= Version("2.14.0"):
        hiddenimports += ['ml_dtypes']

binaries = []
excludedimports = excluded_submodules

# Suppress warnings for missing hidden imports generated by this hook.
# Requires PyInstaller > 5.1 (with pyinstaller/pyinstaller#6914 merged); no-op otherwise.
warn_on_missing_hiddenimports = False

# Collect the AutoGraph part of `tensorflow` code, to avoid a run-time warning about AutoGraph being unavailable:
# `WARNING:tensorflow:AutoGraph is not available in this environment: functions lack code information. ...`
# The warning is emitted if source for `log` function from `tensorflow.python.autograph.utils.ag_logging` cannot be
# looked up. Not sure if we need sources for other parts of `tesnorflow`, though.
# Requires PyInstaller >= 5.3, no-op in older versions.
module_collection_mode = {
    'tensorflow.python.autograph': 'py+pyz',
}

# Linux builds of tensorflow can optionally use CUDA from nvidia-* packages. If we managed to obtain dist, query the
# requirements from metadata (the `and-cuda` extra marker), and convert them to module names.
#
# NOTE: while the installation of nvidia-* packages via `and-cuda` extra marker is not gated by the OS version check,
# it is effectively available only on Linux (last Windows-native build that supported GPU is v2.10.0, and assumed that
# CUDA is externally available).
if is_linux and dist is not None:
    def _infer_nvidia_hiddenimports():
        import packaging.requirements
        from _pyinstaller_hooks_contrib.hooks.utils import nvidia_cuda as cudautils

        requirements = [packaging.requirements.Requirement(req) for req in dist.requires or []]
        env = {'extra': 'and-cuda'}
        requirements = [req.name for req in requirements if req.marker is None or req.marker.evaluate(env)]

        return cudautils.infer_hiddenimports_from_requirements(requirements)

    try:
        nvidia_hiddenimports = _infer_nvidia_hiddenimports()
    except Exception:
        # Log the exception, but make it non-fatal
        logger.warning("hook-tensorflow: failed to infer NVIDIA CUDA hidden imports!", exc_info=True)
        nvidia_hiddenimports = []
    logger.info("hook-tensorflow: inferred hidden imports for CUDA libraries: %r", nvidia_hiddenimports)
    hiddenimports += nvidia_hiddenimports


# Collect the tensorflow-plugins (pluggable device plugins)
hiddenimports += ['tensorflow-plugins']
binaries += collect_dynamic_libs('tensorflow-plugins')
