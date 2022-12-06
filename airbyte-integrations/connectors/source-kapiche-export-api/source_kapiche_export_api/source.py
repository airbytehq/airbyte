from abc import ABC, abstractmethod
from pathlib import Path
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
import pandas as pd
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class KapicheExportApiStream(HttpStream, ABC):
    """
    Abstract Stream class for kapiche-export-api connector.
    All streams from airbyte must inherit from this as a base class.
    """

    def __init__(self, authenticator: HttpAuthenticator = None):
        super().__init__(authenticator)
        self._url_base = ''

    @property
    def url_base(self) -> str:
        """
        :return: URL base for the  API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "https://myapi.com/v1/"
        """
        return self._url_base

    @url_base.setter
    def url_base(self, value:str):
        self._url_base =  value


class ExportDataGet(KapicheExportApiStream, ABC):
    """
    Export Stream to get the actual data from analysis. This is the base class for all then
    enabled exports for a connection. The schema and name for each Stream instance is defined
    dynamically, according to the analysis name and project name.
    """

    primary_key = None
    cursor_field = 'document_id__'
    
    def __init__(
        self,
        export_uuid: str,
        authenticator: HttpAuthenticator,
        url: str = "",
        name: str = None,
        site_name: str = "",
        vertical_themes: bool = False,
        theme_level_separator: str = '',
    ):

        self._session = requests.Session()
        self._authenticator = authenticator
        self.export_uuid = export_uuid
        self._cursor_value = 1
        self._url_base = url
        self._name = name
        self.site_name = site_name
        self.vertical_themes = vertical_themes
        self.theme_level_separator = theme_level_separator

    # needed to instantiate the class
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, str]]:
        if x := response.headers.get('Kapiche-next-document-id'):
            return { self.cursor_field: x}
        else:
            return None

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return f'kapiche-{self._name}'
    
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        if current_stream_state.get(self.cursor_field):
            if int(current_stream_state[self.cursor_field]) < int(latest_record[self.cursor_field]):
                return {self.cursor_field: latest_record[self.cursor_field]}
            else:
                return {self.cursor_field: current_stream_state[self.cursor_field]}

        return self.state

    def path(self, *args, **kwargs) -> str:
        """
        Returns the URL path for the endpoint. 
        """
        return f"document-queries/"
    
    @property
    def cursor_field(self) -> str:
        """
        This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return 'document_id__'

    @property
    def schemaPath(self) -> Path:
        return Path(f'./{self.name}-schema.json') 

    @property
    def state(self) -> Mapping[str, int]:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
       self._cursor_value = value[self.cursor_field]

    def _get_df_from_response(self, response: requests.Response) -> pd.DataFrame:
        """Return a dataframe from a response object containg all the data"""
        fname = f'export_file_{self.path}.parquet'
        with open(fname, 'wb') as file:
            file.write(response.content)

        return pd.read_parquet(fname)

    def request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        """ Add the required headers for the request. """
        return {'Site-Name': self.site_name}

    def request_params(
        self,
        start_document_id: int = 1,
        docs_count: int = 50000,
        export_format: str = 'parquet',
    ) -> MutableMapping[str, Any]:
        """ Request Parameters to configure export. """
        params = {
            'start_document_id': start_document_id,
            'docs_count': docs_count,
            'export_format': export_format,
            'vertical-themes': self.vertical_themes,
            'theme-level-separator': self.theme_level_separator,
        }

        return params
    
    def request_kwargs(
        self,
        stream:bool,
        *args,
        **kwargs,
    ) -> dict[str, Any]:
        options = dict(super().request_kwargs(stream_state=self.state, *args, **kwargs))
        options['stream'] = stream
        return options

    def get_json_schema(self) -> Mapping[str, Any]:
        """Dynamically create the schema for this stream usinf the list endpoint."""
        if self.schemaPath.exists():
            with open(self.schemaPath, 'r') as fp:
                schema = json.load(fp)
            return schema

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "document_id__": {
                "type": ["null", "integer"]
                }
            }
        }
        request = self._create_prepared_request(
            path=self.path(),
            headers={ **self.request_headers(), **self.authenticator.get_auth_header()},
            params=self.request_params(start_document_id=1, docs_count=2),
        )
        request_kwargs = self.request_kwargs(stream=True)
        response = self._send_request(request, request_kwargs)
        df = self._get_df_from_response(response)
        
        for col in df.columns:
            dtype = df[col].dtype
            if pd.api.types.is_integer_dtype(dtype):
                schema['properties'][col] = {"type": ["null", "integer"]}
            if pd.api.types.is_float_dtype(dtype):
                schema['properties'][col] = {"type": ["null", "number"]}
            if pd.api.types.is_datetime64_any_dtype(df[col].dtype):
                # According to airbyte docs, we need to choose formats with either with or without timezone
                # information. Since currently we donot get any timezone info from the product,
                # we choose to use 'timezone_withouttimestamp' format.
                # https://docs.airbyte.com/understanding-airbyte/supported-data-types/
                schema['properties'][col] = {"type": ["null", "string"], "format":"timestamp_without_timezone"}
            else:
                schema['properties'][col] = {"type": ["null", "string"]}
        with open(self.schemaPath, 'w+') as schema_file:
            json.dump(schema, schema_file)
        return schema

    def parse_response(
        self,
        response: requests.Response,
        fname: Path,
        **kwargs
    ) -> Iterable[Mapping]:
        """
        Consume the response streaming content to create a parquet file, and return Mapping data from this
        generated file.
        """
        with open(fname, 'wb') as file:
            for content in response.iter_content(chunk_size=None):
                file.write(content)
        df = pd.read_parquet(fname)

        # Substitute all NaNs with "null", otherwise the row will fail Json conversion.
        df.fillna("null", inplace=True)
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col].dtype):
                df[col] = df[col].dt.strftime(date_format='%Y-%m-%dT%H:%M:%S%z')

        data_json = df.reset_index().to_dict(orient='records')
        yield from data_json

    def read_records(
        self,
        *args,
        **kwargs,
    ) -> Iterable[Mapping[str, Any]]:
        fname = Path(f'./export_file_{self.path}.parquet')
        next_doc = self._cursor_value

        while True:
            request_headers = self.request_headers()
            request = self._create_prepared_request(
                path=self.path(),
                headers={ **request_headers, **self.authenticator.get_auth_header()},
                params=self.request_params(start_document_id=next_doc),
            )
            request_kwargs = self.request_kwargs(stream=True)

            response = self._send_request(request, request_kwargs)
            if response.status_code == 204:
                break
            for record in  self.parse_response(response, fname):
                yield record

            next_doc = response.headers.get('Kapiche-next-document-id')
            self._cursor_value = next_doc

        fname.unlink(missing_ok=True)
        self.schemaPath.unlink(missing_ok=True)
        # Always return an empty generator just in case no records were ever yielded
        yield from []    


class ExportDataList(KapicheExportApiStream):
    """
    Get all the analysis from the `list` endpoint for a given site.
    """
    
    primary_key = None

    def __init__(
        self,
        authenticator: HttpAuthenticator = None,
        url: str = None,
    ):
        super().__init__(authenticator)
        self._url_base = url

    # needed to instantiate the class
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return super().next_page_token(response)

    def path(
        self, **kwargs
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "/export-list/"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json


# Basic incremental stream
class IncrementalKapicheExportApiStream(KapicheExportApiStream, ABC):
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

# Source
class SourceKapicheExportApi(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Connection check to validate that the config can be used to connect to the Export API.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        auth = TokenAuthenticator(token=config["api_token"], auth_method='Site')
        export_list_stream = ExportDataList(authenticator=auth, url=config['export_api_url'])

        request = export_list_stream._create_prepared_request(
            path='export/list/',
            headers={ 'Site-Name': config['site_name'], **auth.get_auth_header()}
        )
        response = export_list_stream._send_request(request, {})

        if response.status_code != 200:
            return False, Exception(f'Received {response.status_code=} from export/list/ endpoint.')

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[ExportDataGet]:
        """
        Calls the 'list' endpoint to return streams for all active analysis exports for the site configured.
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        # Call the list endpoint and get all the exports available
        auth = TokenAuthenticator(token=config["api_token"], auth_method='Site')
        export_list_stream = ExportDataList(authenticator=auth, url=config['export_api_url'])

        request = export_list_stream._create_prepared_request(
            path='export/list/',
            headers={"Site-Name":config["site_name"], **auth.get_auth_header()}
        )
        response = export_list_stream._send_request(request, {})

        if response.status_code != 200:
            raise Exception('List endpoint request failed!!')

        data = response.json()
        export_list = [
            ExportDataGet(
                export['uuid'],
                auth,
                export['export_url'],
                f"{export['project_name']}-{export['analysis_name']}",
                config['site_name'],
                config['vertical_themes'],
                config['theme_level_separator'],
            )
            for export in data if export.get('enabled')
        ]
        
        return export_list
