import yaml
from dagster import Output, asset

GROUP_NAME = "dev"

@asset(required_resource_keys={"metadata_file_directory"}, group_name=GROUP_NAME)
def persist_metadata_definitions(context, catalog_derived_metadata_definitions):
    files = []
    for metadata in catalog_derived_metadata_definitions:
        connector_dir_name = metadata["data"]["dockerRepository"].replace("airbyte/", "")
        definitionId = metadata["data"]["definitionId"]

        key = f"{connector_dir_name}-{definitionId}"

        yaml_string = yaml.dump(metadata)

        file = context.resources.metadata_file_directory.write_data(yaml_string.encode(), ext="yaml", key=key)
        files.append(file)

    file_paths = [file.path for file in files]
    file_paths_str = "\n".join(file_paths)

    return Output(files, metadata={"count": len(files), "file_paths": file_paths_str})
