#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import shutil
from pathlib import Path
from subprocess import check_call

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.install import install


def check_singer():
    tmp_dir = "/tmp/singer-python"
    if not os.path.exists(tmp_dir):
        check_call(f"git clone -b v5.8.1 https://github.com/singer-io/singer-python.git {tmp_dir}".split())
    setup_py = Path(tmp_dir) / "setup.py"
    setup_py.write_text(setup_py.read_text().replace("jsonschema==", "jsonschema>="))
    setup_py.write_text(setup_py.read_text().replace("backoff==", "backoff>="))
    setup_py.write_text(setup_py.read_text().replace("requests==", "backoff>="))
    check_call(f"pip install -U  {tmp_dir}".split())


class CustomInstallCommand(install):
    def run(self):
        check_singer()
        install.run(self)
        if os.path.exists("/tmp/singer-python"):
            shutil.rmtree("/tmp/singer-python")


class CustomDevelopCommand(develop):
    def run(self):
        check_singer()
        develop.run(self)
        if os.path.exists("/tmp/singer-python"):
            shutil.rmtree("/tmp/singer-python")


class CustomEggInfoCommand(egg_info):
    def run(self):
        check_singer()
        egg_info.run(self)
        if os.path.exists("/tmp/singer-python"):
            shutil.rmtree("/tmp/singer-python")


MAIN_REQUIREMENTS = ["airbyte-cdk", "tap-kustomer==1.0.2"]

TEST_REQUIREMENTS = ["pytest~=6.1"]

setup(
    name="source_kustomer_singer",
    description="Source implementation for Kustomer, built on the Singer tap implementation.",
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
