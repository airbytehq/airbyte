#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import dagger


def get_container_dockerfile(container) -> str:
    """Returns the Dockerfile of the base image container.
    Disclaimer: THIS IS HIGHLY EXPERIMENTAL, HACKY AND BRITTLE.
    TODO: CONFIRM WITH THE DAGGER TEAM WHAT CAN GO WRONG HERE.
    Returns:
        str: The Dockerfile of the base image container.
    """
    lineage = [
        field for field in list(container._ctx.selections) if isinstance(field, dagger.api.base.Field) and field.type_name == "Container"
    ]
    dockerfile = []
    for field in lineage:
        if field.name == "from":
            dockerfile.append(f'FROM {field.args.get("address")}')
        if field.name == "withExec":
            dockerfile.append(f'RUN {" ".join(field.args.get("args"))}')  # type: ignore
        if field.name == "withEnvVariable":
            dockerfile.append(f'ENV {field.args.get("name")}={field.args.get("value")}')
        if field.name == "withLabel":
            dockerfile.append(f'LABEL {field.args.get("name")}={field.args.get("value")}')
    return "\n".join(dockerfile)
