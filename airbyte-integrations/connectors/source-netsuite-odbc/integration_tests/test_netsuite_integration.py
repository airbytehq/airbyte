import pytest
import json
import os
import logging
from source_netsuite_odbc.source import SourceNetsuiteOdbc
from sys import platform
import subprocess

def get_integration_path(file_name):
  file_dir = os.path.dirname(os.path.realpath('__file__'))
  final_path = os.path.join(file_dir, file_name)
  if final_path.startswith('/' + file_name):
    final_path = os.path.join('/airbyte/integration_code', final_path[1:])
  return final_path


@pytest.fixture
def config_one():
  file_dir = os.path.dirname(os.path.realpath('__file__'))
  final_path = os.path.join(file_dir, 'secrets/config.json')
  f = open(final_path)
  return json.load(f)

@pytest.fixture
def configured_catalog_one():
  final_path = get_integration_path('integration_tests/configured_catalog.json')
  f = open(final_path)
  return json.load(f)

@pytest.fixture
def configured_catalog_two():
  file_dir = os.path.dirname(os.path.realpath('__file__'))
  final_path = os.path.join(file_dir, 'integration_tests/configured_catalog_two.json')
  print(final_path)
  f = open(final_path)
  return json.load(f)



def test_integration(config_one, configured_catalog_one):
  source = SourceNetsuiteOdbc()
  logger =  logging.getLogger("airbyte")
  read_results = source.read(logger, config_one, configured_catalog_one)
  for result in read_results:
    assert result == ''