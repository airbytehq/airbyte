from sgqlc.operation import Operation
from sgqlc.types import Type, Field, list_of, ID, Input


class Viewer(Type):
    id = ID
    searchWorkspaces = Field('WorkspaceConnection', args={'query': str})

class Workspace(Type):
    id = ID
    name = str
    repositoriesConnection = Field('RepositoryConnection')
    pipelinesConnection = Field('PipelineConnection', args={'first': int})


class WorkspaceConnection(Type):
    nodes = list_of('Workspace')

class RepositoryConnection(Type):
    nodes = list_of('Repository')

class Repository(Type):
    id = ID
    name = str

class PipelineConnection(Type):
    nodes = list_of('Pipeline')

class Pipeline(Type):
    id = ID
    name = str

class SearchIssues(Type):
    totalCount = int
    nodes = list_of('Issue')

class PipelineIssue(Type):
    pipeline = Field('Pipeline')
    priority = Field('Priority')

class Issue(Type):
    id = ID
    ghId = str
    title = str
    type = str
    body = str
    state = str
    createdAt = str
    updatedAt = str
    pipelineIssue = Field(PipelineIssue, args={'workspaceId': ID})

class Filters(Input):
    repositoryIds = list_of(ID)
    pipelineIds = list_of(ID)

class Priority(Type):
    id = ID
    name = str

class Query(Type):
    viewer = Field(Viewer)
    workspace = Field(Workspace, args={'id': ID}) 
    searchIssues = Field(SearchIssues, args={
        'workspaceId': ID
        , 'filters': Filters
    })
