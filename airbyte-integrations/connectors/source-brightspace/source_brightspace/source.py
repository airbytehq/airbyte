#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from email import message
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import re
from urllib.parse import unquote
import zipfile
import os
import csv
import json

# Basic full refresh stream
class BrightspaceStream(HttpStream, ABC):
    # TODO: Fill in the url base. Required
    url_base = "https://nyptest.brightspace.com/d2l/api/lp/"
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def set_base_url(self, url):
        self.url_base = url

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def create_folder_if_not_exists(folder_path):
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Folder '{folder_path}' created.")
            else:
                print(f"Folder '{folder_path}' already exists.")

        except PermissionError as pe:
            print(f"Error: PermissionError - {pe}")
        except OSError as ose:
            print(f"Error: OSError - {ose}")
        except Exception as e:
            print(f"An unexpected error occurred while creating the folder: {e}")

    
    def url_decode(input_string):
        try:
            decoded_string = unquote(input_string)
            return decoded_string

        except UnicodeDecodeError as ude:
            print(f"Error: UnicodeDecodeError - {ude}")
        except Exception as e:
            print(f"An unexpected error occurred during URL decoding: {e}")
            return None

    def read_csv_file(file_path):
        try:
            with open(file_path, 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile)
                data = ""
                for row in csv_reader:
                    data += ', '.join(row) + '\n'
                return data
        except FileNotFoundError:
            return f"File '{file_path}' not found."
        except Exception as e:
            return f"An error occurred while reading the file '{file_path}': {e}"
    
    def unzip_file(zip_file_path, extraction_path):
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extraction_path)
                extracted_files = zip_ref.namelist()
        except zipfile.BadZipFile as bzfe:
            print(f"Error: Bad Zip File - {bzfe}")
        except zipfile.LargeZipFile as lzfe:
            print(f"Error: Large Zip File - {lzfe}")
        except zipfile.PatoolError as pe:
            print(f"Error: Patool Error - {pe}")
        except Exception as e:
            print(f"An unexpected error occurred during extraction: {e}")

        return extracted_files

    def delete_file(file_path):
        try:
            os.remove(file_path)
            print(f"File '{file_path}' has been deleted.")
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
        except Exception as e:
            print(f"An error occurred while deleting the file '{file_path}': {e}")
   
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield {}


# Basic incremental stream
class IncrementalBrightspaceStream(BrightspaceStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}

class Lists(BrightspaceStream):

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.version = config['version']
        self.api_key = config['api_key']

    primary_key = None
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        url = self.version + "/dataExport/list"
        return url
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # The api requires that we include apikey as a header so we do that in this method
        return {'Authorization': 'Bearer ' + self.api_key}
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()

class BdsDownloadPluginid(BrightspaceStream):

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        BrightspaceStream.set_base_url(self, config['url_base'])
        self.version = config['version']
        self.api_key = config['api_key']
        self.plugin_id = config['plugin_id']
        self.file_path = config['file_path']
        BrightspaceStream.create_folder_if_not_exists(self.file_path)

    primary_key = None
    
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        url = self.version + "i" + self.plugin_id
        return url
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # The api requires that we include apikey as a header so we do that in this method
        return {'Authorization': 'Bearer ' + self.api_key}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Check if 'content-disposition' header exists in the response headers
        if 'content-disposition' in response.headers:
            url = re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
            url = url.replace('"', '')
            url = BrightspaceStream.url_decode(url)
            url = self.file_path + url
            try:
                with open(url, 'wb') as out:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            out.write(chunk)
            except Exception as e:
                print(f"An error occurred while writing to the file: {e}")
            
            print(" Zip file downloaded successfully ")
            
            # unzip the file
            extracted_files = BrightspaceStream.unzip_file(url, self.file_path)
            
            # delete the zip file now
            BrightspaceStream.delete_file(url)
            
            result = ''
            for file in extracted_files:
                result += BrightspaceStream.read_csv_file(self.file_path + "/" + file)
                BrightspaceStream.delete_file(self.file_path + "/" + file)

            data = {"result" : result}
            json_like = json.dumps(data)
            
            response._content = json_like.encode('utf-8')
            return [response.json()]
        else:
            print("'content-disposition' header not found in response headers.")
            return []

    
# Source
class SourceBrightspace(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [BdsDownloadPluginid(config=config)]
