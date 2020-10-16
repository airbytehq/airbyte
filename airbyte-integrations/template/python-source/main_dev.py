from airbyte_protocol.entrypoint import launch
from template_python_source import TemplatePythonSource

if __name__ == "__main__":
    source = TemplatePythonSource()
    launch(source, ["spec"])
