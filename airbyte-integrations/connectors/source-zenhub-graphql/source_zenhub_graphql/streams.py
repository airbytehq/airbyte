from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple


import requests, json
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level

from sgqlc.endpoint.http import HTTPEndpoint 
from sgqlc.operation import Operation
from sgqlc.types import Type, Field, list_of

from .utils import log

from .graphql import (
    Viewer
    , Query
    , WorkspaceConnection
    , Workspace as WSGraphql
    , Repository
    , RepositoryConnection
    , Pipeline
    , PipelineConnection
    , PipelineIssue
    , Issue
    , SearchIssues
    , Priority
)


# Basic full refresh stream
class ZenhubGraphqlStream(HttpStream, ABC):

    url_base = "https://api.zenhub.com/public/graphql"

    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class ZenhubGraphqlStream(HttpStream, ABC)` which is the current class
    `class Customers(ZenhubGraphqlStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(ZenhubGraphqlStream)` contains behavior to pull data for employees using v1/employees
    """
    #WITH sgqlc method HTTPEndpoint
    #class ZenhubGraphqlStream(HTTPEndpoint, ABC):
    #def __init__(self,api_key: str, url_base: str="https://api.zenhub.com/public/graphql", **kwargs):
    #    self.headers = {'Authorization': f'Bearer {api_key}'}
    #    super().__init__(url_base, self.headers, **kwargs) 

    @property
    def http_method(self) -> str:
        return "POST"
    

    def __init__(self, api_key: str, **kwargs):
        super().__init__(authenticator=TokenAuthenticator(token=api_key),**kwargs) 

    def request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        return { "Content-Type": "application/json"
                , **super().request_headers(*args, **kwargs)
                }

    def request_body_json(self, *args, **kwargs) -> Optional[Mapping]:
        pass

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
       
        return {}
    
    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        
        #Uncomment to see Logs
        #log(Level.INFO, f"Full Request Object: {request.__dict__}")
        log(Level.INFO, f"Sending request to URL: {request.url}")
        #log(Level.INFO, f"Request headers: {request.headers}")
        log(Level.INFO, f"Request body: {request.body}")
        
        response = super()._send_request(request, request_kwargs)
        
        log(Level.INFO, f"Response status code: {response.status_code}")
        log(Level.INFO, f"Response text: {response.text}")
        
        return response
        
    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any], next_page_token: Mapping[str, Any] = None,**kwargs) -> Iterable[Mapping]:
        if response.status_code != 200:
            raise Exception(f"Query failed with status code {response.status_code}: {response.text}")
        else:
            json_response = response.json()
            data = json_response.get("data", [])
        return data


class ZenhubWorkspace(ZenhubGraphqlStream):

    def __init__(self, api_key, workspace_name):
        super().__init__(api_key)
        self.workspace_name = workspace_name
    
    def get_ws_query(self):
        ws_op = Operation(Query)
        viewer_query = ws_op.viewer
        viewer_query.id()
        ws_op_query = viewer_query.searchWorkspaces(query=self.workspace_name)
        workspace_node = ws_op_query.nodes.__as__(WSGraphql)  # Use the Workspace type
        workspace_node.id()
        workspace_node.name()
        repository_node = workspace_node.repositoriesConnection.nodes.__as__(Repository)
        repository_node.id()
        repository_node.name()
        return str(ws_op)
    
    def request_body_json(self, *args, **kwargs) -> Optional[Mapping]:
        query = self.get_ws_query()

        #Uncomment to see logs
        #log(Level.INFO, f"Raw Query: {query}")
        return {"query": query}
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Parse the JSON response
        response_json = response.json()

        # Handle any errors in the response
        if 'errors' in response_json:
            raise Exception(f"Errors in response: {response_json['errors']}")

        # Extract the data from the response
        data = response_json.get('data', {})

        # Iterate over the records and yield them
        for record in self.extract_records(data):
            print(record)
            yield record
    
    def extract_records(self, data: Mapping) -> Iterable[Mapping]:
        # The top level key to start iteration
        viewer_data = data.get('viewer', {})

        # Iterate through each workspace node
        for workspace in viewer_data.get('searchWorkspaces', {}).get('nodes', []):
            workspace_id = workspace.get('id') #Extracts the workspace of that specific record
            # Extract repository data from each workspace
            for repo in workspace.get('repositoriesConnection', {}).get('nodes', []):
                # Yield a dictionary with the repository ID and name
                yield {
                        'workspace_id': workspace_id
                        ,'repo_id': repo.get('id')
                        , 'repo_name': repo.get('name')}
       
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        pass
    
    @property
    def primary_key(self):
        pass

class ZenhubPipelines(ZenhubGraphqlStream):
    """
    Stream to fetch pipeline IDs from a specific workspace.
    """
    def __init__(self, api_key, workspace_id):
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_pipelines_query(self):
        pipeline_op = Operation(Query)
        workspace_query = pipeline_op.workspace(id=self.workspace_id)
        workspace_query.id()
        pipelines = workspace_query.pipelinesConnection(first=50).nodes
        pipelines.id()
        pipelines.name()
        #log(Level.INFO, f"PIPELINE FORMED: {pipeline_op}")
        return str(pipeline_op)

    def request_body_json(self, *args, **kwargs) -> Optional[Mapping]:
        query = self.get_pipelines_query()
        log(Level.INFO, f"Pipeline Query: {query}")
        return {"query": query}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()

        if 'errors' in response_json:
            raise Exception(f"Errors in response: {response_json['errors']}")

        data = response_json.get('data', {})

        for pipeline in data.get('workspace', {}).get('pipelinesConnection', {}).get('nodes', []):
            yield { 'workspace_id': self.workspace_id
                    , 'pipeline_id': pipeline.get('id')
                    , 'pipeline_name': pipeline.get('name')}
        
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        pass
    
    @property
    def primary_key(self):
        pass


class ZenhubIssues(ZenhubGraphqlStream):
    def __init__(self, api_key, workspace_id, repo_ids, pipeline_ids):
        super().__init__(api_key)
        self.workspace_id = workspace_id
        self.repo_ids = repo_ids
        self.pipeline_ids = pipeline_ids

    def get_issues_query(self):
        issues_op = Operation(Query)
        issues_query = issues_op.searchIssues(
            workspaceId=self.workspace_id, 
            filters={
                'repositoryIds': self.repo_ids 
                , 'pipelineIds': self.pipeline_ids

            }
        )
        issues_query.totalCount()
        issue_node = issues_query.nodes.__as__(Issue)
        issue_node.id()
        issue_node.ghId()
        issue_node.title()
        issue_node.type()
        issue_node.body()
        issue_node.state()
        issue_node.createdAt()
        issue_node.updatedAt()
        pipeline_issue = issue_node.pipelineIssue(workspaceId=self.workspace_id)
        pipeline = pipeline_issue.pipeline
        pipeline.id()
        pipeline.name()
        priority = pipeline_issue.priority
        priority.id()
        priority.name()
        return str(issues_op)

    def request_body_json(self, *args, **kwargs) -> Optional[Mapping]:
        query = self.get_issues_query()
        log(Level.INFO, f"Issues Query: {query}")
        return {"query": query}
    
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        pass
    
    @property
    def primary_key(self):
        pass

# Basic incremental stream
class IncrementalZenhubGraphqlStream(ZenhubGraphqlStream, ABC):
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

