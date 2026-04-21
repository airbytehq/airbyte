---
id: airbyte_agent_sdk-connectors-clickup_api-types
title: airbyte_agent_sdk.connectors.clickup_api.types
---

Module airbyte_agent_sdk.connectors.clickup_api.types
=====================================================
Type definitions for clickup-api connector.

Classes
-------

`CommentsCreateParams(*args, **kwargs)`
:   Parameters for comments.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: int`
    :   The type of the None singleton.

    `comment_text: str`
    :   The type of the None singleton.

    `notify_all: bool`
    :   The type of the None singleton.

    `task_id: str`
    :   The type of the None singleton.

`CommentsGetParams(*args, **kwargs)`
:   Parameters for comments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_id: str`
    :   The type of the None singleton.

`CommentsListParams(*args, **kwargs)`
:   Parameters for comments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `task_id: str`
    :   The type of the None singleton.

`CommentsUpdateParams(*args, **kwargs)`
:   Parameters for comments.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: int`
    :   The type of the None singleton.

    `comment_id: str`
    :   The type of the None singleton.

    `comment_text: str`
    :   The type of the None singleton.

    `resolved: bool`
    :   The type of the None singleton.

`DocsGetParams(*args, **kwargs)`
:   Parameters for docs.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `doc_id: str`
    :   The type of the None singleton.

    `workspace_id: str`
    :   The type of the None singleton.

`DocsListParams(*args, **kwargs)`
:   Parameters for docs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `workspace_id: str`
    :   The type of the None singleton.

`FoldersGetParams(*args, **kwargs)`
:   Parameters for folders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `folder_id: str`
    :   The type of the None singleton.

`FoldersListParams(*args, **kwargs)`
:   Parameters for folders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `space_id: str`
    :   The type of the None singleton.

`GoalsGetParams(*args, **kwargs)`
:   Parameters for goals.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `goal_id: str`
    :   The type of the None singleton.

`GoalsListParams(*args, **kwargs)`
:   Parameters for goals.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `team_id: str`
    :   The type of the None singleton.

`ListsGetParams(*args, **kwargs)`
:   Parameters for lists.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `list_id: str`
    :   The type of the None singleton.

`ListsListParams(*args, **kwargs)`
:   Parameters for lists.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `folder_id: str`
    :   The type of the None singleton.

`MembersListParams(*args, **kwargs)`
:   Parameters for members.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `task_id: str`
    :   The type of the None singleton.

`SpacesGetParams(*args, **kwargs)`
:   Parameters for spaces.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `space_id: str`
    :   The type of the None singleton.

`SpacesListParams(*args, **kwargs)`
:   Parameters for spaces.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `team_id: str`
    :   The type of the None singleton.

`TasksApiSearchParams(*args, **kwargs)`
:   Parameters for tasks.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignees: list[str]`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `date_created_gt: int`
    :   The type of the None singleton.

    `date_created_lt: int`
    :   The type of the None singleton.

    `date_updated_gt: int`
    :   The type of the None singleton.

    `date_updated_lt: int`
    :   The type of the None singleton.

    `due_date_gt: int`
    :   The type of the None singleton.

    `due_date_lt: int`
    :   The type of the None singleton.

    `include_closed: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `priority: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `statuses: list[str]`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

`TasksGetParams(*args, **kwargs)`
:   Parameters for tasks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `custom_task_ids: bool`
    :   The type of the None singleton.

    `include_subtasks: bool`
    :   The type of the None singleton.

    `task_id: str`
    :   The type of the None singleton.

`TasksListParams(*args, **kwargs)`
:   Parameters for tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `list_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

`TeamsListParams(*args, **kwargs)`
:   Parameters for teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`TimeTrackingGetParams(*args, **kwargs)`
:   Parameters for time_tracking.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `team_id: str`
    :   The type of the None singleton.

    `time_entry_id: str`
    :   The type of the None singleton.

`TimeTrackingListParams(*args, **kwargs)`
:   Parameters for time_tracking.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: str`
    :   The type of the None singleton.

    `end_date: int`
    :   The type of the None singleton.

    `start_date: int`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

`UserGetParams(*args, **kwargs)`
:   Parameters for user.get operation

    ### Ancestors (in MRO)

    * builtins.dict

`ViewTasksListParams(*args, **kwargs)`
:   Parameters for view_tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `view_id: str`
    :   The type of the None singleton.

`ViewsGetParams(*args, **kwargs)`
:   Parameters for views.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `view_id: str`
    :   The type of the None singleton.

`ViewsListParams(*args, **kwargs)`
:   Parameters for views.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `team_id: str`
    :   The type of the None singleton.