import importlib.metadata

airbyte_lib_version = importlib.metadata.version("airbyte-lib")

def get_version():
    return airbyte_lib_version