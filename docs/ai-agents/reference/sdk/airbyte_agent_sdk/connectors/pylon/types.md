---
id: airbyte_agent_sdk-connectors-pylon-types
title: airbyte_agent_sdk.connectors.pylon.types
---

Module airbyte_agent_sdk.connectors.pylon.types
===============================================
Type definitions for pylon connector.

Classes
-------

<a id="AccountsCreateParams"></a>

`AccountsCreateParams(*args, **kwargs)`
:   Parameters for accounts.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `domains: list[str]`
    :   The type of the None singleton.

    `logo_url: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `owner_id: str`
    :   The type of the None singleton.

    `primary_domain: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

<a id="AccountsGetParams"></a>

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AccountsListParams"></a>

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="AccountsUpdateParams"></a>

`AccountsUpdateParams(*args, **kwargs)`
:   Parameters for accounts.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `domains: list[str]`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `is_disabled: bool`
    :   The type of the None singleton.

    `logo_url: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `owner_id: str`
    :   The type of the None singleton.

    `primary_domain: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

<a id="ArticlesCreateParams"></a>

`ArticlesCreateParams(*args, **kwargs)`
:   Parameters for articles.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_user_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `is_published: bool`
    :   The type of the None singleton.

    `kb_id: str`
    :   The type of the None singleton.

    `slug: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="ArticlesUpdateParams"></a>

`ArticlesUpdateParams(*args, **kwargs)`
:   Parameters for articles.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `kb_id: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="CollectionsCreateParams"></a>

`CollectionsCreateParams(*args, **kwargs)`
:   Parameters for collections.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `kb_id: str`
    :   The type of the None singleton.

    `slug: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="ContactsCreateParams"></a>

`ContactsCreateParams(*args, **kwargs)`
:   Parameters for contacts.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `avatar_url: str`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="ContactsGetParams"></a>

`ContactsGetParams(*args, **kwargs)`
:   Parameters for contacts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ContactsListParams"></a>

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="ContactsUpdateParams"></a>

`ContactsUpdateParams(*args, **kwargs)`
:   Parameters for contacts.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="CustomFieldsGetParams"></a>

`CustomFieldsGetParams(*args, **kwargs)`
:   Parameters for custom_fields.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CustomFieldsListParams"></a>

`CustomFieldsListParams(*args, **kwargs)`
:   Parameters for custom_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `object_type: str`
    :   The type of the None singleton.

<a id="IssueNotesCreateParams"></a>

`IssueNotesCreateParams(*args, **kwargs)`
:   Parameters for issue_notes.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_html: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `message_id: str`
    :   The type of the None singleton.

    `thread_id: str`
    :   The type of the None singleton.

<a id="IssueThreadsCreateParams"></a>

`IssueThreadsCreateParams(*args, **kwargs)`
:   Parameters for issue_threads.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="IssuesCreateParams"></a>

`IssuesCreateParams(*args, **kwargs)`
:   Parameters for issues.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `assignee_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `priority: str`
    :   The type of the None singleton.

    `requester_email: str`
    :   The type of the None singleton.

    `requester_name: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="IssuesGetParams"></a>

`IssuesGetParams(*args, **kwargs)`
:   Parameters for issues.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="IssuesListParams"></a>

`IssuesListParams(*args, **kwargs)`
:   Parameters for issues.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `end_time: str`
    :   The type of the None singleton.

    `start_time: str`
    :   The type of the None singleton.

<a id="IssuesUpdateParams"></a>

`IssuesUpdateParams(*args, **kwargs)`
:   Parameters for issues.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `assignee_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

<a id="MeGetParams"></a>

`MeGetParams(*args, **kwargs)`
:   Parameters for me.get operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="MessagesListParams"></a>

`MessagesListParams(*args, **kwargs)`
:   Parameters for messages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="MilestonesCreateParams"></a>

`MilestonesCreateParams(*args, **kwargs)`
:   Parameters for milestones.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `due_date: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

<a id="MilestonesUpdateParams"></a>

`MilestonesUpdateParams(*args, **kwargs)`
:   Parameters for milestones.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `due_date: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="ProjectsCreateParams"></a>

`ProjectsCreateParams(*args, **kwargs)`
:   Parameters for projects.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `description_html: str`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

<a id="ProjectsUpdateParams"></a>

`ProjectsUpdateParams(*args, **kwargs)`
:   Parameters for projects.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description_html: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `is_archived: bool`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="TagsCreateParams"></a>

`TagsCreateParams(*args, **kwargs)`
:   Parameters for tags.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hex_color: str`
    :   The type of the None singleton.

    `object_type: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="TagsGetParams"></a>

`TagsGetParams(*args, **kwargs)`
:   Parameters for tags.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TagsListParams"></a>

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="TagsUpdateParams"></a>

`TagsUpdateParams(*args, **kwargs)`
:   Parameters for tags.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hex_color: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="TasksCreateParams"></a>

`TasksCreateParams(*args, **kwargs)`
:   Parameters for tasks.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `due_date: str`
    :   The type of the None singleton.

    `milestone_id: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="TasksUpdateParams"></a>

`TasksUpdateParams(*args, **kwargs)`
:   Parameters for tasks.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="TeamsCreateParams"></a>

`TeamsCreateParams(*args, **kwargs)`
:   Parameters for teams.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="TeamsGetParams"></a>

`TeamsGetParams(*args, **kwargs)`
:   Parameters for teams.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TeamsListParams"></a>

`TeamsListParams(*args, **kwargs)`
:   Parameters for teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="TeamsUpdateParams"></a>

`TeamsUpdateParams(*args, **kwargs)`
:   Parameters for teams.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="TicketFormsListParams"></a>

`TicketFormsListParams(*args, **kwargs)`
:   Parameters for ticket_forms.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="UserRolesListParams"></a>

`UserRolesListParams(*args, **kwargs)`
:   Parameters for user_roles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.