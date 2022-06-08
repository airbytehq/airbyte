#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import inflection
import pytest


@pytest.mark.usefixtures("inputs")
class BaseTest:
    @pytest.fixture(autouse=True)
    def update_run_context(self, docker_runner):
        docker_runner.set_cassette_context(type(self).__name__)

    @classmethod
    def config_key(cls):
        """Name of the test in configuration file, used to override test inputs,"""
        class_name = cls.__name__
        if class_name.startswith("Test"):
            class_name = class_name[len("Test") :]
        return inflection.underscore(class_name)
