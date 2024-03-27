# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
from typing import Dict, Set

from pydantic import BaseModel, Field, validator


class AirbyteCiPackageConfiguration(BaseModel):
    poe_tasks: Set[str] = Field(..., description="List of unique poe tasks to run")
    required_environment_variables: Set[str] = Field(
        set(), description="List of unique required environment variables to pass to the container running the poe task"
    )
    poetry_extras: Set[str] = Field(set(), description="List of unique poetry extras to install")
    optional_poetry_groups: Set[str] = Field(set(), description="List of unique poetry groups to install")
    side_car_docker_engine: bool = Field(
        False, description="Flag indicating the use of a sidecar Docker engine during the poe task executions"
    )
    mount_docker_socket: bool = Field(
        False,
        description="Flag indicating the mount of the host docker socket to the container running the poe task, useful when the package under test is using dagger",
    )

    @validator("required_environment_variables")
    def check_required_environment_variables_are_set(cls, value: Set) -> Set:
        for required_env_var in value:
            if required_env_var not in os.environ:
                raise ValueError(f"Environment variable {required_env_var} is not set.")
        return value


def deserialize_airbyte_ci_config(pyproject_toml: Dict) -> AirbyteCiPackageConfiguration:
    try:
        airbyte_ci_config = pyproject_toml["tool"]["airbyte_ci"]
    except KeyError:
        raise ValueError("Missing tool.airbyte_ci configuration in pyproject.toml")
    return AirbyteCiPackageConfiguration.parse_obj(airbyte_ci_config)
