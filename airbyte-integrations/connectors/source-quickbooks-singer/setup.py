#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import os
import shutil
from pathlib import Path
from subprocess import check_call

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.install import install

TMP_DIR = "/tmp/singer-python"


def check_singer():
    if not os.path.exists(TMP_DIR):
        check_call(f"git clone -b v5.12.1 --depth 1 https://github.com/singer-io/singer-python.git {TMP_DIR}".split())
    setup_py = Path(TMP_DIR) / "setup.py"
    setup_py.write_text(setup_py.read_text().replace("jsonschema==", "jsonschema~="))
    setup_py.write_text(setup_py.read_text().replace("backoff==", "backoff>="))
    # setup_py.write_text(setup_py.read_text().replace("requests==", "backoff>="))
    #print(setup_py.read_text())
    #check_call(f"git switch -c v5.12.1".split())
    #check_call(f"pip install -U {TMP_DIR}".split())
    

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
    "pytest~=6.1",
    "source-acceptance-test",
]

setup(
    name="source_quickbooks_singer",
    description="Source implementation for Quickbooks, built on the Singer tap implementation.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    cmdclass={
        "install": CustomInstallCommand,
        "develop": CustomDevelopCommand,
        "egg_info": CustomEggInfoCommand,
    },
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
