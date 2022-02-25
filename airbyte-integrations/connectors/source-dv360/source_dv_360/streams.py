
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from xmlrpc.client import Boolean

import pendulum
from airbyte_cdk.sources.streams import Stream
from typing import Tuple
import json
import os
from datetime import datetime
from typing import Dict, Generator, Mapping, Any, List
import pendulum
from  google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from datetime import timedelta
from contextlib import closing
from six.moves.urllib.request import urlopen
import pandas as pd
import io
import csv

REPORT_TYPE_MAPPING = {
    "audience_composition": "TYPE_AUDIENCE_COMPOSITION",
    "cookie_reach": "TYPE_REACH_AND_FREQUENCY",
    "floodlight": "FLOODLIGHT",
    "standard": "TYPE_GENERAL",
    "unique_reach_audience": "TYPE_REACH_AUDIENCE",
    "unique_reach": "TYPE_REACH_AND_FREQUENCY"
}

class DBM:
  QUERY_TEMPLATE_PATH = "source_dv_360/queries/query_template.json"
  DBM_SCOPE = 'doubleclickbidmanager'

  def __init__(self, credentials: Credentials, partner_id: str, scope: str = DBM_SCOPE, version: str = 'v1.1'):
    self.service = build(scope,version, credentials= credentials)
    self.partner_id = partner_id

  def set_partner_filter(self,query: Mapping[str, Any]):
    #print(query)
    filters = query.get("params").get("filters")
    if filters:
      partner_filter_index = next((index for (index, filter) in enumerate(filters) if filter["type"] == "FILTER_PARTNER"), None)
      if partner_filter_index is not None:
        query["params"]["filters"][partner_filter_index]["value"] = self.partner_id

  def create_query_object(self, report_name:str, dimensions:List[str], metrics:List[str],
    start_date_ms:str, end_date_ms:str, filters:List[dict] = [] ) -> Mapping[str, Any]:
    """
    Create a query object from the template and a list of dimensions and metrics
    """
    with open(DBM.QUERY_TEMPLATE_PATH, 'r') as template:
      query_body = json.loads(template.read())

    self.set_partner_filter(query_body) #Set partner Id in the filter
    query_body["metadata"]["title"] = report_name
    query_body["params"]["type"] = REPORT_TYPE_MAPPING[report_name]
    query_body["params"]["groupBys"] = dimensions
    query_body["params"]["filters"].extend(filters)
    query_body["params"]["metrics"] = metrics
    query_body["reportDataStartTimeMs"] = start_date_ms
    query_body["reportDataEndTimeMs"] = end_date_ms
    return query_body


  def get_dimensions_from_schema(self, schema: Mapping[str, Any]) -> List[str]:
    """
    Return a list of dimensions from the givem schema
    """
    dimensions = [key for key in schema.get("properties").keys() if key.startswith('FILTER')]
    return dimensions

  def get_metrics_from_schema(self, schema: Mapping[str, Any]) -> List[str]:
    """
    Return a list of metrics from the givem schema
    """
    metrics = [key for key in schema.get("properties").keys() if key.startswith('METRIC')]
    return metrics

  def get_report_type_from_schema(self, schema: Mapping[str, Any]) -> str:
    """
    Return the report type from the given schema
    """
    properties = schema.get("properties")
    return list(properties.get("params").get("report_type"))

  def convert_schema_into_query(self,schema: Mapping[str, Any], report_name: str, start_date: str, end_date: str = None) -> str:
    """
    Create a query from the given schema
    """
    start_date = pendulum.parse(start_date)
    end_date = pendulum.parse(end_date) if end_date else pendulum.yesterday()
    query = self.create_query_object(
      report_name = report_name,
      dimensions = self.get_dimensions_from_schema(schema),
      metrics = self.get_metrics_from_schema(schema),
      start_date_ms = str(int(start_date.timestamp() * 1000)),   ## Convert dates to ms --> checkeck for timezone
      end_date_ms = str(int(end_date.timestamp() * 1000)),
    )
    print(query)
    create_query =self.service.queries().createquery(body=query).execute()
    get_query=self.service.queries().getquery(queryId=create_query.get('queryId')).execute()
    print(get_query)
    return get_query


class DBMStream(Stream, ABC):
  """
  Base stream class
  """
  OUTPUT_DIR = "source_dv_360/reports"

  def __init__(self, credentials: Credentials, partner_id: str, start_date: str, end_date: str=None):
    self.dbm = DBM(credentials= credentials, partner_id=partner_id)
    self._start_date = start_date
    self._end_date = end_date

  def get_query(self, stream_slice:Mapping[str, Any] ) -> Iterable[Mapping]:
    """
    Return a query
    """
    query = self.dbm.convert_schema_into_query(schema= self.get_json_schema(), report_name= self.name,
    start_date=self._start_date, end_date=self._end_date)
    return query

  def fetch_report(self, query: dict, output_dir: str = OUTPUT_DIR) -> str:
    """
    Fetch a report and save the CSV file in the reports directory
    """
    output_file = ""
    query_id = query.get("queryId")
    print(query_id)
    if query_id:
      try:
        if not os.path.isabs(output_dir):
          output_dir = os.path.expanduser(output_dir)
          # Grab the report and write contents to a file.
          report_url = query['metadata']['googleCloudStoragePathForLatestReport']
          output_file = '%s/%s.csv' % (output_dir, query['queryId'])
          with open(output_file, 'wb') as output:
            with closing(urlopen(report_url)) as url:
              output.write(url.read())
          print('Download complete.')
        else:
          print('No reports for queryId "%s"' %query['queryId'])
      except KeyError:
        print('No report found for queryId "%s".' % query_id)
    else:
      print('No queries exist.')
    return output_file


  def file_reader(self,filename):
    """
    Read file until an empty line is encountered
    """
    with open(filename) as f:
      for line in f:
        if line and line != '\n':
          yield line
        else:
          break

  def get_list_of_columns(self,csv_file_path:str) -> List[str]:
    """
    Get the list of columns from a csv file, which are the header of the file
    """
    with open(csv_file_path, 'r') as csvfile:
      reader = csv.reader(csvfile)
      field_names_list = next(reader)
    return field_names_list

  def read_records(self, stream_slice: Mapping[str, Any]=None,sync_mode=None, **kwargs) -> Iterable[Mapping[str, Any]]:
    """
    Read records and store them in json
    """
    report_file= self.fetch_report(self.get_query(stream_slice))
    if report_file != "":
      data = io.StringIO(''.join(self.file_reader(report_file)))
      final_data = pd.read_csv(data)
      json_data = final_data.to_json(orient='records',lines=True)
      print(json_data)
      return json_data
    else:
      return {}


class DBMIncrementalStream(DBMStream, ABC):
  cursor_field = "" # ToDo

  def __init__(self, start_date: str, end_date: str=None, **kwargs):
    self._start_date = start_date
    self._end_date = end_date
    super().__init__(**kwargs)


class AudienceComposition(DBMStream):
  """
  Audience Composition stream
  """


class CookieReach(DBMStream):
  """
  Cookie Reach stream
  """
  primary_key = None

class Floodlight(DBMStream):
  """
  Floodlight stream
  """

class Standard(DBMStream):
  """
  Standard stream
  """
  primary_key = None

class UniqueReachAudience(DBMStream):
  """
  Unique Reach Audience stream
  """
  primary_key = None

class UniqueReach(DBMStream):
  """
  Unique Reach stream
  """
  primary_key = None
