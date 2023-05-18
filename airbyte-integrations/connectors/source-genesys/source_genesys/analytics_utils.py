import hashlib
import json
from datetime import datetime
from source_genesys.analytics_models import AnalyticsMetric

from airbyte_cdk.logger import init_logger


def generate_query(window_date_str: str, metrics: list[str]):
    """
    :param metrics: The list of metrics to query.
    :param window_date_str: The window date string to query against. Format: YYYY-MM-DD
    :return: Rendered Genesys analytics API query
    """
    logger = init_logger()
    query = {
        "interval": f"{window_date_str}T00:00:00.000Z/{window_date_str}T23:59:59.000Z",
        "metrics": metrics
    }
    logger.debug(f"Rendered new analytics query:\n{json.dumps(query, indent=2)}")

    return query


def create_surrogate_key(*argv) -> str:
    """
    Get surrogate key value from n cols.
    :param argv: n columns to build the surrogate key with
    :return: a hased surrogate key unique identifier str
    """
    surr_key_str = ""
    for key in argv:
        surr_key_str += str(key)

    surr_key = hashlib.md5(surr_key_str.encode("utf-8")).hexdigest()
    return surr_key


def str_timestamp_to_datetime(timestamp_value):
    """
    Function that converts a string or datetime value to a datetime object.
    :param timestamp_value: str/datetime value
    :return: datetime value or None
    """
    logger = init_logger()
    if isinstance(timestamp_value, str):
        try:
            return datetime.strptime(timestamp_value, '%Y-%m-%d')
        except ValueError:
            logger.exception(f"Invalid string format: {timestamp_value}")
    elif isinstance(timestamp_value, datetime):
        return timestamp_value
    else:
        logger.exception(f"Cannot convert type: {type(timestamp_value)} to datetime!")
        return timestamp_value


def split_utc_timestamp_interval(timestamp_range_str: str):
    """
    Split a string interval value into start and end datetime values.
    :param timestamp_range_str: An interval string timestamp value split by '/' in the following format:
        YYYY-MM-DDThh:mm:ss/YYYY-MM-DDThh:mm:ss
    :return: tuple containing the values: start_datetime, end_datetime
    """
    start, end = timestamp_range_str.split('/')
    start_datetime = datetime.fromisoformat(start.rstrip('Z'))
    end_datetime = datetime.fromisoformat(end.rstrip('Z'))
    return start_datetime, end_datetime


def parse_analytics_records(client_id: str, results_json: dict[str, any]):
    """
    Traverse through the different metric groups within the response
    and validate the record model against AnalyticsMetric() dataclass.
    :param results_json:
    :yield: generator
    """
    logger = init_logger()

    for metric_group in results_json:

        # Retrieve the start/end timestamps from the interval value
        interval = metric_group["data"][0]["interval"]
        start_timestamp, end_timestamp = split_utc_timestamp_interval(interval)

        # Loop through each nested metric in JSON
        for metric in metric_group["data"][0]["metrics"]:

            # Create unique_id via surrogate_key (client_id+media_type+interval_end+metric)
            uid = create_surrogate_key(
                client_id,
                metric_group["group"]["mediaType"],
                end_timestamp,
                metric["metric"]
            )
            # Flatten metric results into individual records
            metric_record = AnalyticsMetric(
                uid=uid,
                client_id=client_id,
                media_type=metric_group["group"]["mediaType"],
                interval_start=start_timestamp,
                interval_end=end_timestamp,
                metric_name=metric["metric"],
                max=metric.get("stats").get("max", None),
                min=metric.get("stats").get("min", None),
                count=metric.get("stats").get("count", None),
                sum=metric.get("stats").get("sum", None),
            ).dict()
        
            logger.debug(f"metric record: {metric_record}")
            yield metric_record

