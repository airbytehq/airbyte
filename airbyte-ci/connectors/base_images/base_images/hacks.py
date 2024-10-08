#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dagger

# If we perform addition dagger operations on the container, we need to make sure that a mapping exists for the new field name.
DAGGER_FIELD_NAME_TO_DOCKERFILE_INSTRUCTION = {
    "from": lambda field: f'FROM {field.args.get("address")}',
    "withExec": lambda field: f'RUN {" ".join(field.args.get("args"))}',
    "withEnvVariable": lambda field: f'ENV {field.args.get("name")}={field.args.get("value")}',
    "withLabel": lambda field: f'LABEL {field.args.get("name")}={field.args.get("value")}',
}


def get_container_dockerfile(container) -> str:
    """Returns the Dockerfile of the base image container.
    Disclaimer: THIS IS HIGHLY EXPERIMENTAL, HACKY AND BRITTLE.
    TODO: CONFIRM WITH THE DAGGER TEAM WHAT CAN GO WRONG HERE.
    Returns:
        str: The Dockerfile of the base image container.
    """
    lineage = [
        field
        for field in list(container._ctx.selections)
        if isinstance(field, dagger.client._core.Field) and field.type_name == "Container"
    ]
    dockerfile = []

    for field in lineage:
        if field.name in DAGGER_FIELD_NAME_TO_DOCKERFILE_INSTRUCTION:
            try:
                dockerfile.append(DAGGER_FIELD_NAME_TO_DOCKERFILE_INSTRUCTION[field.name](field))
            except KeyError:
                raise KeyError(
                    f"Unknown field name: {field.name}, please add it to the DAGGER_FIELD_NAME_TO_DOCKERFILE_INSTRUCTION mapping."
                )
    return "\n".join(dockerfile)
