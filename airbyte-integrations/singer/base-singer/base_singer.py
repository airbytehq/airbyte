# todo: we can use something like this instead of fixed file names
# import importlib.util
# import os
#
# airbyte_singer_source_path = os.environ['AIRBYTE_SINGER_SOURCE_PATH']
# airbyte_singer_source_module = os.environ['AIRBYTE_SINGER_SOURCE_MODULE']
#
# spec = importlib.util.spec_from_file_location(airbyte_singer_source_module, airbyte_singer_source_path)
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)
# module.MyClass()

from source_implementation import SourceImplementation
from singer_source import SingerSource

source = SourceImplementation()
source.__class__ = SingerSource
