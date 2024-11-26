#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
Decorators for skipping PyInstaller tests when specific requirements are not met.
"""

import distutils.ccompiler
import inspect
import os
import shutil
import textwrap

import pytest
import sys

from PyInstaller.compat import is_win
from PyInstaller.utils.hooks import check_requirement

# Wrap some pytest decorators to be consistent in tests.
parametrize = pytest.mark.parametrize
skipif = pytest.mark.skipif
xfail = pytest.mark.xfail


def _check_for_compiler():
    import tempfile

    # Change to some tempdir since cc.has_function() would compile into the current directory, leaving garbage.
    old_wd = os.getcwd()
    tmp = tempfile.mkdtemp()
    os.chdir(tmp)
    cc = distutils.ccompiler.new_compiler()
    if is_win:
        try:
            cc.initialize()
            has_compiler = True
        # This error is raised on Windows if a compiler can't be found.
        except distutils.errors.DistutilsPlatformError:
            has_compiler = False
    else:
        # The C standard library contains the ``clock`` function. Use that to determine if a compiler is installed. This
        # does not work on Windows::
        #
        #   Users\bjones\AppData\Local\Temp\a.out.exe.manifest : general error
        #   c1010070: Failed to load and parse the manifest. The system cannot
        #   find the file specified.
        has_compiler = cc.has_function('clock', includes=['time.h'])
    os.chdir(old_wd)
    # TODO: Find a way to remove the generated clockXXXX.c file, too
    shutil.rmtree(tmp)
    return has_compiler


# A decorator to skip tests if a C compiler is not detected.
has_compiler = _check_for_compiler()
skipif_no_compiler = skipif(not has_compiler, reason="Requires a C compiler")

skip = pytest.mark.skip


def importorskip(package: str):
    """
    Skip a decorated test if **package** is not importable.

    Arguments:
        package:
            The name of the module. May be anything that is allowed after the ``import`` keyword. e.g. 'numpy' or
            'PIL.Image'.
    Returns:
        A pytest marker which either skips the test or does nothing.

    This function intentionally does not import the module. Doing so can lead to `sys.path` and `PATH` being
    polluted, which then breaks later builds.
    """
    if not importable(package):
        return pytest.mark.skip(f"Can't import '{package}'.")
    return pytest.mark.skipif(False, reason=f"Don't skip: '{package}' is importable.")


def importable(package: str):
    from importlib.util import find_spec

    # The find_spec() function is used by the importlib machinery to locate a module to import. Using it finds the
    # module but does not run it. Unfortunately, it does import parent modules to check submodules.
    if "." in package:
        # Using subprocesses is slow. If the top level module doesn't exist then we can skip it.
        if not importable(package.split(".")[0]):
            return False
        # This is a submodule, import it in isolation.
        from subprocess import DEVNULL, run
        return run([sys.executable, "-c", "import " + package], stdout=DEVNULL, stderr=DEVNULL).returncode == 0

    return find_spec(package) is not None


def requires(requirement: str):
    """
    Mark a test to be skipped if **requirement** is not satisfied.

    Args:
        requirement:
            A distribution name and optional version specifier(s). See :func:`PyInstaller.utils.hooks.check_requirement`
            which this argument is forwarded to.
    Returns:
        Either a skip marker or a dummy marker.

    This function operates on distribution metadata, and does not import any modules.
    """
    if check_requirement(requirement):
        return pytest.mark.skipif(False, reason=f"Don't skip: '{requirement}' is satisfied.")
    else:
        return pytest.mark.skip(f"Requires {requirement}.")


def gen_sourcefile(tmpdir, source, test_id=None):
    """
    Generate a source file for testing.

    The source will be written into a file named like the test-function. This file will then be passed to
    `test_script`. If you need other related file, e.g. as `.toc`-file for testing the content, put it at at the
    normal place. Just mind to take the basnename from the test-function's name.

    :param script: Source code to create executable from. This will be saved into a temporary file which is then
                   passed on to `test_script`.

    :param test_id: Test-id for parametrized tests. If given, it will be appended to the script filename,
                    separated by two underscores.

    Ensure that the caller of `test_source` is in a UTF-8 encoded file with the correct '# -*- coding: utf-8 -*-'
    marker.
    """
    testname = inspect.stack()[1][3]
    if test_id:
        # For parametrized test append the test-id.
        testname = testname + '__' + test_id

    # Periods are not allowed in Python module names.
    testname = testname.replace('.', '_')
    scriptfile = tmpdir / (testname + '.py')
    source = textwrap.dedent(source)
    with scriptfile.open('w', encoding='utf-8') as ofh:
        print('# -*- coding: utf-8 -*-', file=ofh)
        print(source, file=ofh)
    return scriptfile
