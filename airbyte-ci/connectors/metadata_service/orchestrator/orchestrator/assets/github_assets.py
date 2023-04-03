from dagster import Output, asset

GROUP_NAME = "github"


@asset(required_resource_keys={"github_connectors_directory"}, group_name=GROUP_NAME)
def github_connector_folders(context):
    """
    Return a list of all the folders in the github connectors directory.
    """
    github_connectors_directory = context.resources.github_connectors_directory

    folder_names = [item.name for item in github_connectors_directory if item.type == "dir"]
    return Output(folder_names, metadata={"preview": folder_names})
