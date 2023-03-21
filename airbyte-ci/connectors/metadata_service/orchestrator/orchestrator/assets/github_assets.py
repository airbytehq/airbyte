from dagster import MetadataValue, Output, asset, OpExecutionContext

@asset(required_resource_keys={"github_connectors_directory"})
def source_controlled_connectors(context):
    github_connectors_directory = context.resources.github_connectors_directory

    folder_names = [item.name for item in github_connectors_directory if item.type == 'dir']
    return folder_names;
    # return Output(folder_names, metadata={'preview': folder_names})
