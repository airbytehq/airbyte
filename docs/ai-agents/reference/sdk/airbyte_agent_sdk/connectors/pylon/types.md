---
id: airbyte_agent_sdk-connectors-pylon-types
title: airbyte_agent_sdk.connectors.pylon.types
---

Module airbyte_agent_sdk.connectors.pylon.types
===============================================
Type definitions for pylon connector.

Classes
-------

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

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

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

`ContactsGetParams(*args, **kwargs)`
:   Parameters for contacts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

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

`CustomFieldsGetParams(*args, **kwargs)`
:   Parameters for custom_fields.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`CustomFieldsListParams(*args, **kwargs)`
:   Parameters for custom_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `object_type: str`
    :   The type of the None singleton.

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

`IssueThreadsCreateParams(*args, **kwargs)`
:   Parameters for issue_threads.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

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

`IssuesGetParams(*args, **kwargs)`
:   Parameters for issues.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

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

`MeGetParams(*args, **kwargs)`
:   Parameters for me.get operation

    ### Ancestors (in MRO)

    * builtins.dict

`MessagesListParams(*args, **kwargs)`
:   Parameters for messages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

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

`TagsGetParams(*args, **kwargs)`
:   Parameters for tags.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

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

`TeamsCreateParams(*args, **kwargs)`
:   Parameters for teams.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`TeamsGetParams(*args, **kwargs)`
:   Parameters for teams.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`TeamsListParams(*args, **kwargs)`
:   Parameters for teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

`TeamsUpdateParams(*args, **kwargs)`
:   Parameters for teams.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

`TicketFormsListParams(*args, **kwargs)`
:   Parameters for ticket_forms.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

`UserRolesListParams(*args, **kwargs)`
:   Parameters for user_roles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.