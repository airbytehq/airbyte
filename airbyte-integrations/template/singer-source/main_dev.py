import sys
from airbyte_protocol.entrypoint import launch

from template_singer_source import TemplateSingerSource

if __name__ == "__main__":
    source = TemplateSingerSource()
    launch(source, sys.argv[1:])
