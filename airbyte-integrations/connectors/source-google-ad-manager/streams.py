#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from os import stat
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import logging
import time
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from googleads import ad_manager
from googleads.errors import AdManagerReportError

_CHUNK_SIZE = 16 * 1024


logger = logging.getLogger('{}.{}'.format(__name__, 'google_ad_manager_report_downloader'))


class BaseGoogleAdManagerReportStream(HttpStream, ABC):
    """
    TODO remove this comment

    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class GoogleAdManagerStream(HttpStream, ABC)` which is the current class
    `class Customers(GoogleAdManagerStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(GoogleAdManagerStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalGoogleAdManagerStream((GoogleAdManagerStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    def __init__(self, google_ad_manger_client: ad_manager.AdManagerClient) -> None:
        super().__init__()
        self.google_ad_manger_client = google_ad_manger_client
    
    def download_report(self, report_job_id: str, export_format: str, include_report_properties: bool = False,
                        include_totals_row: bool = None, use_gzip_compression: bool = True) -> requests.Response:
        """make an api call to the api with the report job id and return a response containing the report

        Args:
          report_job_id: The ID of the report job to wait for, as a string.
          export_format: The export format for the report file, as a string.
          outfile: A writeable, file-like object to write to.
          include_report_properties: Whether or not to include the report
            properties (e.g. network, user, date generated...)
            in the generated report.
          include_totals_row: Whether or not to include the totals row.
          use_gzip_compression: Whether or not to use gzip compression.
        """
        service = self.google_ad_manger_client._GetReportService()

        if include_totals_row is None:  # True unless CSV export if not specified
            include_totals_row = True if export_format != 'CSV_DUMP' else False
        opts = {
            'exportFormat': export_format,
            'includeReportProperties': include_report_properties,
            'includeTotalsRow': include_totals_row,
            'useGzipCompression': use_gzip_compression
        }
        report_url = service.getReportDownloadUrlWithOptions(report_job_id, opts)
        logger.info('Request Summary: Report job ID: %s, %s', report_job_id, opts)

        response = self.url_opener.open(report_url)
        return response

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        this is the base method to parse the api response
        """
        logger.info("start parsing the response stream, should be replaced with logger")

        while True:
            chunk = response.read(_CHUNK_SIZE)
            if not chunk:
                break
            yield chunk
    
    def run_report(self, report_job):
        """Runs a report, then waits (blocks) for the report to finish generating.

        Args:
          report_job: The report job to wait for. This may be a dictionary or an
              instance of the SOAP ReportJob class.

        Returns:
          The completed report job's ID as a string.

        Raises:
          An AdManagerReportError if the report job fails to complete.
        """
        service = self._GetReportService()
        report_job_id = service.runReportJob(report_job)['id']

        status = service.getReportJobStatus(report_job_id)

        while status != 'COMPLETED' and status != 'FAILED':
            logger.debug('Report job status: %s', status)
            time.sleep(30)
            status = service.getReportJobStatus(report_job_id)

        if status == 'FAILED':
            raise AdManagerReportError(report_job_id)
        else:
            logger.debug('Report has completed successfully')
            return report_job_id
    
    @staticmethod
    def add_dates_ranges(report_job, start_date, end_date):
        """add the start date and the end date to the report job.

        Args:
            report_job (_type_): _description_
            start_date (_type_): _description_
            end_date (_type_): _description_
        """
        if start_date and end_date:
            report_job['reportQuery']['dateRangeType'] = 'CUSTOM_DATE'
            report_job['reportQuery']['startDate'] = start_date
            report_job['reportQuery']['endDate'] = end_date
        else:
            report_job["reportQuery"]["dateRangeType"] = 'YESTERDAY'
        return report_job
    
    @staticmethod
    def convert_time_to_dict(date):
        return {
            'year': date.year,
            'month': date.month,
            'day': date.day}
    
    def generate_report_query(self, start_date, end_date):
        raise NotImplementedError("generate_report_query should be implemented")


class AdUnitPerHourReportStream(BaseGoogleAdManagerReportStream):
    """this class generate the report for the Ad unit PerHour

    Args:
        BaseGoogleAdManagerReportStream (_type_): _description_

    Returns:
        _type_: _description_
    """

    def generate_report_query(self, start_date: dict, end_date: dict) -> dict:
        """generate the report query for the ad unit per hour report

        Returns:
            _type_: _description_
        """
        columns = ["TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS",
                   "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                   "TOTAL_LINE_ITEM_LEVEL_CLICKS",
                   "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE",
                   "TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM",
                   "TOTAL_LINE_ITEM_LEVEL_CTR",
                   "TOTAL_CODE_SERVED_COUNT"]
        dimensions = ['AD_UNIT_NAME', 'HOUR', "DATE"]
        report_job = {"reportQuery": {}}
        report_job['reportQuery']['dimensions'] = dimensions
        report_job['reportQuery']['columns'] = columns
        report_job["reportQuery"]["adUnitView"] = 'HIERARCHICAL'
        report_job = self.add_dates_ranges(report_job, start_date, end_date)
        return report_job
