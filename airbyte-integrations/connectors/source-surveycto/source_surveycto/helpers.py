#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import csv
import json
from datetime import datetime
from io import StringIO

import boto3
import botocore
import pandas as pd
import requests
import smart_open
from bigquery_schema_generator.generate_schema import SchemaGenerator
from gbqschema_converter.gbqschema_to_jsonschema import json_representation as converter
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Helpers(object):
    @staticmethod
    def _base64_encode(string: str) -> str:
        """
        Encodes a string using base64 encoding.

        Args:
            string (str): The string to be encoded.

        Returns:
            str: The base64 encoded string.
        """
        return base64.b64encode(string.encode("ascii")).decode("ascii")

    @staticmethod
    def get_filter_data(data):
        """
        Get the schema for filtering data. This is used to generate Schema dynamically.

        Args:
            data (dict): The input data for schema generation.

        Returns:
            dict: The generated schema for filtering data.
        """
        generator = SchemaGenerator(input_format="dict", infer_mode="NULLABLE", preserve_input_sort_order="true")

        data = [data]
        schema_map, error_logs = generator.deduce_schema(input_data=data)

        schema = generator.flatten_schema(schema_map)

        schema_json = converter(schema)
        schema = schema_json["definitions"]["element"]
        # remove all additionalProperties. This solves the error during acceptance test: ` When set, additionalProperties field value must be true for backward compatibility.`
        for key in schema["properties"]:
            schema["properties"][key]["additionalProperties"] = True
        schema["additionalProperties"] = True
        return schema

    @staticmethod
    def _get_local_urls(file_path, file_name, column):
        """
        Get a list of local URLs from a CSV file.

        Args:
            file_path (str): The path to the directory containing the CSV file.
            file_name (str): The name of the CSV file.
            column (str): The name of the column containing the URLs.

        Returns:
            list: A list of local URLs extracted from the specified column in the CSV file.
        """
        try:
            data = pd.read_csv(f"{file_path}{file_name}")
            return data[column].tolist()
        except Exception as e:
            raise e
            # raise Exception("Error reading file. Make sure the file path and name are correct.")

    @staticmethod
    def _get_s3_urls(aws_access_key_id, aws_secret_access_key, source_name, region_name, file_key, column):
        """
        Retrieve a list of Urls from a specific column in a CSV file stored in an S3 bucket.

        Args:
            aws_access_key_id (str): The AWS access key ID.
            aws_secret_access_key (str): The AWS secret access key.
            source_name (str): The name of the S3 bucket.
            region_name (str): The AWS region name.
            file_key (str): The key of the file in the S3 bucket.
            column (str): The name of the column to retrieve urls from.

        Returns:
            list: A list of urls from the specified column in the CSV file.

        Raises:
            Exception: If there is an error retrieving the object from the S3 bucket.

        """
        try:
            aws_access_key_id = aws_access_key_id
            aws_secret_access_key = aws_secret_access_key
            bucket_name = source_name
            s3 = boto3.client(
                "s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name
            )

            response = s3.get_object(Bucket=bucket_name, Key=file_key)
            result = None
            # Ensure the object is received
            status_code = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if status_code == 200:
                # Read the CSV content
                csv_string = response["Body"].read().decode("utf-8")

                # Use StringIO to convert the CSV string to a file-like object so pandas can read it
                csv_file = StringIO(csv_string)

                # Create a pandas DataFrame from the file-like object
                result = pd.read_csv(csv_file)
                # print(result[column, file_name, file_type])

                return result[column].tolist()
            else:
                # Handle errors or a non-200 status code
                raise Exception(f"Error getting object {file_key} from bucket {bucket_name}. Make sure the bucket and key are correct.")

        except Exception as e:
            raise e

    @staticmethod
    def fetch_records(url, auth_basic, key, type):
        """
        Fetches records from a SurveyCTO using the specified authentication and data format.

        Args:
            url (str): The URL to fetch the records from.
            auth_basic (tuple): A tuple containing the username and password for basic authentication.
            key (str): The key that was used to encrypt the data.
            type (str): The format of the data to be fetched ("json" or "csv").

        Returns:
            list: A list of records fetched from the URL.

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs during the request.

        """
        http = requests.Session()
        default_headers = {
            "X-OpenRosa-Version": "1.0",
        }
        data = []
        try:
            if key == "key" or key == "" or key is None:
                response = http.get(url, headers=default_headers, auth=auth_basic)
                response.raise_for_status()

                if type == "json":
                    data = response.json()
                else:
                    csv_file = StringIO(response.text)
                    # Read the CSV data
                    reader = csv.DictReader(csv_file)

                    # Convert to JSON
                    data = list(reader)

            else:
                files = {"private_key": key}
                response = requests.post(url, files=files, headers=default_headers, auth=auth_basic)
                response.raise_for_status()

                data = response.json()
                if type == "json":
                    data = response.json()
                else:
                    csv_file = StringIO(response.text)
                    # Read the CSV data
                    reader = csv.DictReader(csv_file)

                    # Convert to JSON
                    data = list(reader)

        except requests.exceptions.HTTPError as e:
            raise e
        except Exception as e:
            raise e

        return data

    @staticmethod
    def format_date(date_string):
        """
        Formats a date string in the format "%Y-%m-%dT%H:%M:%S%z" to "%b %d, %Y %I:%M:%S %p" format.

        Args:
            date_string (str): The date string to be formatted.

        Returns:
            str: The formatted date string.

        Raises:
            Exception: If the date string is in the wrong format.
        """
        try:
            formatted_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
            formatted_date_string = formatted_date.strftime("%b %d, %Y %I:%M:%S %p")
            return formatted_date_string

        except Exception as e:
            raise Exception("Wrong date format. Check Example ")

    @staticmethod
    def login(config):
        """
        Logs in to the SurveyCTO server using the provided configuration.

        Args:
            config (dict): A dictionary containing the server_name, username, and password.

        Returns:
            bool: True if the login is successful, False otherwise.
        """
        server_name = config["server_name"]
        url = f"https://{server_name}.surveycto.com"

        _sesh = requests.session()
        try:
            response = _sesh.head(url)
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise e

        headers = {"X-csrf-token": response.headers["X-csrf-token"]}
        auth_basic = requests.auth.HTTPBasicAuth(config["username"], config["password"])
        auth = _sesh.post(
            url + "/login",
            cookies=_sesh.cookies,
            headers=headers,
            auth=auth_basic,
        )

        if auth.status_code == 200:
            return True
        else:
            return False
