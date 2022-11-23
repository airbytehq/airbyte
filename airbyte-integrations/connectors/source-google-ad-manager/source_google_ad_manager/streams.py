#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional, List
import logging
import time
from pathlib import Path
import pandas as pd
from pendulum import parse as pendulum_parse, now as pendulum_now
from pendulum.tz.zoneinfo.exceptions import InvalidTimezone
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from googleads import ad_manager
from googleads.errors import AdManagerReportError
from typing import Any, Mapping, Union, List
import tempfile
from .data_classes import AdUnitPerHourItem, AdUnitPerReferrerItem, ReportStatus
from .utils import convert_time_to_dict

CHUNK_SIZE = 16 * 1024
API_VERSION = 'v202208'
TIMEOUT_LIMIT = 60*10
EXPORT_FORMAT = 'CSV_DUMP'

logger = logging.getLogger('{}.{}'.format(__name__, 'google_ad_manager_report_downloader'))


class BaseGoogleAdManagerReportStream(Stream, IncrementalMixin):
    """
    this is the base stream class used to generate the report
    """

    def __init__(self, google_ad_manager_client: ad_manager.AdManagerClient, start_date: str, timezone: str) -> None:
        super().__init__()
        self.google_ad_manager_client = google_ad_manager_client
        self.report_downloader = self.google_ad_manager_client.GetDataDownloader(version=API_VERSION)
        self.start_date = start_date
        self.timezone = timezone
        try:
            self.start_date = pendulum_parse(self.start_date).date()
            self.today_date = pendulum_now(timezone).date()
        except InvalidTimezone:
            raise InvalidTimezone(f"Timezone {timezone} is not supported by pendulum, please use a valid timezone")

    @property
    def state(self) -> Mapping[str, Any]:
        if getattr(self, '_cursor_value', None):
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self.today_date.strftime('%Y-%m-%d')}

    @property
    def cursor_field(self) -> str:
        """
        Name of the field in the API response body used as cursor.
        """
        return "date"
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def download_report(self, report_job_id: str) -> str:
        """given the report job id download the report,
         save it in a temporary file and return the file name of the report"""
        report_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv.gz')
        self.report_downloader.DownloadReportToFile(report_job_id, EXPORT_FORMAT, report_file)
        report_file.close()
        logger.info('Report job with id "%s" downloaded to:\n%s' % (report_job_id, report_file.name))
        return Path(report_file.name)

    def build_report_dataframe(self, report_file: str) -> List[Mapping[str, Any]]:
        """take the report file and return a pandas dataframe

        Args:
            report_file (str): path of the report file

        Returns:
            Pd.Dataframe:  dataframe of the report
        """
        report_df = pd.read_csv(report_file, compression='gzip', header=0, sep=',', quotechar='"')
        report_file.unlink(missing_ok=True)
        return report_df
    
    def update_cursor(self, max_date, current_cursor_value):
        """update the cursor value

        Args:
            max_date (str): _description_
            current_cursor_value (str): _description_
        """
        upcoming_cursor_value = pendulum_parse(max_date)
        cursor_value = (max(upcoming_cursor_value, current_cursor_value)).to_date_string()
        max_cursor_value = {self.cursor_field: cursor_value}
        self.state = max_cursor_value

    def parse_response(self, report_dataframe, **kwargs) -> Iterable[Mapping]:
        """
        generate airbyte records from the report dataframe
        
        """
        current_cursor_value = pendulum_parse(self.state.get(self.cursor_field))
        max_date = report_dataframe["Dimension.DATE"].max()
        for row in report_dataframe.to_dict(orient='records'):
            item = self.generate_item(row)
            yield item.dict()
        self.update_cursor(max_date, current_cursor_value)

    def run_report(self, report_job: str) -> str:
        """Runs a report, then waits (blocks) for the report to finish generating.

        Args:
          report_job: The report job to wait for. This may be a dictionary or an
              instance of the SOAP ReportJob class.

        Returns:
          The completed report job's ID as a string.

        Raises:
          An AdManagerReportError if the report job fails to complete.
        """
        service = self.report_downloader._GetReportService()
        report_job_id = service.runReportJob(report_job)['id']

        status = service.getReportJobStatus(report_job_id)
        while status != ReportStatus.COMPLETED.value and status != ReportStatus.FAILED.value:
            logger.debug('Report job status: %s', status)
            time.sleep(30)
            status = service.getReportJobStatus(report_job_id)

        if status == ReportStatus.FAILED.value:
            raise AdManagerReportError(report_job_id)
        else:
            logger.debug('Report has completed successfully')
            return report_job_id
    
    @staticmethod
    def add_dates_ranges(report_job, start_date: Mapping[str, int], end_date: Mapping[str, int]) -> Mapping[str, Any]:
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
    
    @abstractmethod
    def generate_report_query(self, start_date, end_date):
        raise NotImplementedError("generate_report_query should be implemented")
    
    @abstractmethod
    def generate_item(self, row):
        raise NotImplementedError("generate_item should be implemented")
    
    def get_query(self, report_job: Mapping[str, Any]) -> str:
        """convenience method to the generate the URl

        Args:
            stream_slice (Mapping[str, Any]): _description_

        Returns:
            str: _description_
        """
        return self.run_report(report_job)

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """the main method that read the records from the report"""
        try:
            report_job_id = self.get_query(self.report_job)
            report_file = self.download_report(report_job_id)
            report_dataframe = self.build_report_dataframe(report_file)
            yield from self.parse_response(report_dataframe, **kwargs)
        except AdManagerReportError as exc:
            # the error handling should be implemented here, for now raise
            raise exc
        logger.info(f"finished reading the records, the state is{self.state}")
    

class AdUnitPerHourReportStream(BaseGoogleAdManagerReportStream):
    """this class generate the report for the Ad unit PerHour

    Args:
        BaseGoogleAdManagerReportStream (_type_): _description_

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

    def __init__(self, google_ad_manager_client: ad_manager.AdManagerClient, customer_name: str, start_date: str, timezone: str) -> None:
        super().__init__(google_ad_manager_client, start_date, timezone)
        self.customer_name = customer_name
        last_date_pulled = pendulum_parse(self.state.get(self.cursor_field))
        last_date_pulled = last_date_pulled.subtract(days=1)  # just to make sure we are pulling the data for the last day, and have all the value corrected
        logger.warn(f"the last date pulled is ..................... {last_date_pulled}")
        start_date = convert_time_to_dict(last_date_pulled)
        end_date = convert_time_to_dict(self.today_date)
        self.report_job = self.generate_report_query(start_date=start_date, end_date=end_date)

    def generate_report_query(self, start_date: Mapping, end_date: Mapping) -> Mapping:
        """generate the report query for the ad unit per hour report

        Returns:
            _type_: _description_
        """
        report_job = {"reportQuery": {}}
        report_job['reportQuery']['dimensions'] = self.dimensions
        report_job['reportQuery']['columns'] = self.columns
        report_job["reportQuery"]["adUnitView"] = 'HIERARCHICAL'
        report_job = self.add_dates_ranges(report_job, start_date, end_date)
        return report_job
    
    def generate_item(self, row):
        """from a dict returned by the http request generate item

        Args:
            row (_type_): _description_

        Returns:
            _type_: _description_
        """
        row['customer_name'] = self.customer_name
        try:
            return AdUnitPerHourItem.from_dict(row)
        except Exception as e:
            logger.error(f"error while parsing the row {row}, the error is {e}")
            return None
    
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        :return: string if single primary key,
        list of strings if composite primary key,
        list of list of strings if composite primary key consisting of nested fields.
        If the stream has no primary keys, return None.
        """
        return ["ad_unit", "hour", "date", "customer_name", "ad_unit_id"]


class AdUnitPerReferrerReportStream(BaseGoogleAdManagerReportStream):
    """this class generate report query for the ad unit per referrer

    Args:
        BaseGoogleAdManagerReportStream (_type_): _description_
    """
    columns = [
                "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE",
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                "TOTAL_LINE_ITEM_LEVEL_CLICKS",
                "TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM",
                "TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS",
                "TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS",
                "TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS",
            ]
    dimensions = ['ADVERTISER_NAME', 'CUSTOM_CRITERIA', 'AD_UNIT_ID', "DATE"]
    
    def __init__(self, google_ad_manager_client: ad_manager.AdManagerClient, customer_name: str, start_date:str, timezone:str) -> None:
        super().__init__(google_ad_manager_client, start_date, timezone)
        targeting_values = self.get_custom_targeting_keys_ids("referrer")  # @TODO: I can make this manual instead of getting from the api.
        last_date_pulled = pendulum_parse(self.state.get(self.cursor_field))
        last_date_pulled = last_date_pulled.subtract(days=1)  # just to make sure we are pulling the data for the last day, and have all the value corrected
        start_date = convert_time_to_dict(last_date_pulled)
        end_date = convert_time_to_dict(self.today_date)
        self.customer_name = customer_name
        self.report_job = self.generate_report_query(targeting_values, start_date=start_date, end_date=end_date)

    def generate_report_query(self, targeting_values: List, start_date: Mapping, end_date: Mapping) -> Mapping:
        """generate the report query for the ad unit per referrer report

        Returns:
            _type_: _description_
        """
        targets_ids = [targeting_value['id'] for targeting_value in targeting_values if targeting_value["id"]]
        targets_ids = ", ".join([str(target_id) for target_id in targets_ids])
        report_job = {"reportQuery": {}}
        report_job["reportQuery"]["dimensions"] = self.dimensions
        report_job["reportQuery"]["columns"] = self.columns
        report_job["reportQuery"]["adUnitView"] = 'HIERARCHICAL'
        statement_builder = ad_manager.StatementBuilder(version=API_VERSION)
        statement_builder.Where(f"CUSTOM_TARGETING_VALUE_ID IN ({targets_ids})")
        statement_builder.Limit(None).Offset(None)
        report_job["reportQuery"]["statement"] = statement_builder.ToStatement()
        report_job = self.add_dates_ranges(report_job, start_date, end_date)
        return report_job

    def get_custom_targeting_keys_ids(self, name: str) -> List:
        all_keys = []
        custom_targeting_service = self.google_ad_manager_client.GetService('CustomTargetingService', version=API_VERSION)
        statement_builder = ad_manager.StatementBuilder(version=API_VERSION)
        page_size = ad_manager.SUGGESTED_PAGE_LIMIT
        if name:
            statement_builder = statement_builder.Where("name = :name").WithBindVariable('name', name)
        statement_builder.limit = page_size
        timeout = time.time() + TIMEOUT_LIMIT  # 10 minutes from now
        while True:
            response = custom_targeting_service.getCustomTargetingKeysByStatement(statement_builder.ToStatement())
            if time.time() <= timeout:
                if 'results' in response and len(response['results']):
                    all_keys.extend(response['results'])
                    statement_builder.offset += statement_builder.limit
                else:
                    break
            else:
                break
        customs_target_values = self.get_custom_targeting_values(all_keys)
        return customs_target_values

    def get_custom_targeting_values(self, all_keys: list) -> List:
        """given a list of keys retrieve the custom targeting values

        Args:
            all_keys (list): _description_

        Returns:
            dict: _description_
        """
        targeting_values = list()
        if all_keys:
            statement_builder = ad_manager.StatementBuilder(version=API_VERSION)
            custom_targeting_service = self.google_ad_manager_client.GetService('CustomTargetingService', version=API_VERSION)
            statement = statement_builder.Where("customTargetingKeyId IN ({})".format(",".join([str(key['id']) for key in all_keys])))
            timeout = time.time() + TIMEOUT_LIMIT  # 10 minutes from now
            while True:
                response = custom_targeting_service.getCustomTargetingValuesByStatement(statement.ToStatement())
                if time.time() <= timeout:
                    if 'results' in response and len(response['results']):
                        custom_target_list = self.generate_custom_targeting_dict(response['results'])
                        targeting_values.extend(custom_target_list)
                        statement.offset += statement.limit
                    else:
                        break
                else:
                    break
        logger.info("found {} custom targeting values".format(len(targeting_values)))
        return targeting_values

    def generate_custom_targeting_dict(self, results: Mapping[str, str]) -> List:
        """
        generate custom targeting from results
        """
        custom_target_list = list()
        for custom_targeting_value in results:
            custom_target_dict = {"id": custom_targeting_value['id'],
                                  "name": custom_targeting_value['name'],
                                  "displayName": custom_targeting_value['displayName'],
                                  "customTargetingKeyId": custom_targeting_value['customTargetingKeyId']}
            custom_target_list.append(custom_target_dict)
        return custom_target_list
    
    def generate_item(self, row):
        """from a dict returned by the http request generate item

        Args:
            row (_type_): _description_

        Returns:
            _type_: _description_
        """
        row['customer_name'] = self.customer_name
        try:
            return AdUnitPerReferrerItem.from_dict(row)
        except Exception as e:
            # todo: sometimes null values are returned from the apis, ignoring them now and they will be pulled on the next run
            logger.error(f"error while parsing the row {row}, the error is {e}")
            return None

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        :return: string if single primary key,
        list of strings if composite primary key,
        list of list of strings if composite primary key consisting of nested fields.
        If the stream has no primary keys, return None.
        """
        return ["ad_unit", "referrer", "date", "customer_name", "ad_unit_id", "advertiser_name"]
