#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import os
import shutil
from pathlib import Path
from subprocess import check_call
import os
from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.install import install

TMP_DIR = "/tmp/singer-python"


def check_singer():
    if not os.path.exists(TMP_DIR):
        check_call(f"git clone -b v5.12.1 --depth 1 https://github.com/singer-io/singer-python.git {TMP_DIR}".split())
    setup_py = Path(TMP_DIR) / "setup.py"
    setup_py.write_text(setup_py.read_text().replace("jsonschema==", "jsonschema>="))
    setup_py.write_text(setup_py.read_text().replace("backoff==", "backoff>="))
    # check_call(f"pip install -U  {TMP_DIR}".split())


class CustomInstallCommand(install):
    def run(self):
        check_singer()
        install.run(self)
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)


class CustomDevelopCommand(develop):
    def run(self):
        check_singer()
        develop.run(self)
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)


class CustomEggInfoCommand(egg_info):
    def run(self):
        check_singer()
        egg_info.run(self)
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)


MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "tap-quickbooks @ https://github.com/airbytehq//tap-quickbooks/tarball/v1.0.5-airbyte",
]

TEST_REQUIREMENTS = [
    "pytest>=6.1",
    "source-acceptance-test",
]

def install_requires():
    tmp_dir = Path("/tmp/singer-python")
    if not tmp_dir.is_dir():
        check_call(f"git clone -b v5.12.1 --depth 1 https://github.com/singer-io/singer-python.git {tmp_dir}".split())
    setup_py = Path(tmp_dir) / "setup.py"
    setup_py.write_text(setup_py.read_text().replace("jsonschema==", "jsonschema>="))
    setup_py.write_text(setup_py.read_text().replace("backoff==", "backoff>="))
    check_call(f"pip install {tmp_dir}".split())
    if tmp_dir.is_dir():
        shutil.rmtree(tmp_dir)
    print(f"try to install: {MAIN_REQUIREMENTS}")
    # raise Exception("aaa")
    yield from MAIN_REQUIREMENTS


def tests_extras_require():
    sat_src = Path("../../bases/source-acceptance-test")
    sat_dst = Path("/tmp/source-acceptance-test")
    if sat_src.is_dir():
        if not sat_dst.is_dir():
            shutil.copytree(sat_src, sat_dst)
            setup_py = sat_dst / "setup.py"
            setup_py.write_text(setup_py.read_text().replace("jsonschema~=3.2.0", "jsonschema"))
            check_call(f"pip install  {sat_dst}".split())
    if sat_src.is_dir():
        shutil.rmtree(sat_dst)
    yield from TEST_REQUIREMENTS


class IterableAdapter:
    def __init__(self, iterator_factory):
        self.iterator_factory = iterator_factory

    def __iter__(self):
        return self.iterator_factory()


setup(
    name="source_quickbooks_singer",
    description="Source implementation for Quickbooks, built on the Singer tap implementation.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=IterableAdapter(install_requires),
    # cmdclass={
    #     "install": CustomInstallCommand,
    #     "develop": CustomDevelopCommand,
    #     "egg_info": CustomEggInfoCommand,
    #     'build_ext': specialized_build_ext,
    # },
    package_data={"": ["*.json"]},
    extras_require={
        "tests": IterableAdapter(tests_extras_require),
    },
)
