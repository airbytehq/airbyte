---
id: airbyte_agent_sdk-connectors-gmail-models
title: airbyte_agent_sdk.connectors.gmail.models
---

Module airbyte_agent_sdk.connectors.gmail.models
================================================
Pydantic models for gmail connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Draft"></a>

`Draft(**data: Any)`
:   A Gmail draft message
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `message: Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftCreateParams"></a>

`DraftCreateParams(**data: Any)`
:   Parameters for creating or updating a draft
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `message: airbyte_agent_sdk.connectors.gmail.models.DraftCreateParamsMessage | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftCreateParamsMessage"></a>

`DraftCreateParamsMessage(**data: Any)`
:   The draft message content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `raw: str | Any`
    :   The draft message in RFC 2822 format, base64url encoded

    `thread_id: str | Any`
    :   The thread ID for the draft (for threading in a conversation)

<a id="DraftRef"></a>

`DraftRef(**data: Any)`
:   A lightweight reference to a draft (used in list responses)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `message: Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftSendParams"></a>

`DraftSendParams(**data: Any)`
:   Parameters for sending an existing draft
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftsListResponse"></a>

`DraftsListResponse(**data: Any)`
:   Response from listing drafts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `drafts: list[airbyte_agent_sdk.connectors.gmail.models.DraftRef] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any | None`
    :   The type of the None singleton.

    `result_size_estimate: int | Any | None`
    :   The type of the None singleton.

<a id="DraftsListResultMeta"></a>

`DraftsListResultMeta(**data: Any)`
:   Metadata for drafts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any | None`
    :   The type of the None singleton.

    `result_size_estimate: int | Any | None`
    :   The type of the None singleton.

<a id="GmailAuthConfig"></a>

`GmailAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   Your Google OAuth2 Access Token (optional, will be obtained via refresh)

    `client_id: str | None`
    :   Your Google OAuth2 Client ID

    `client_secret: str | None`
    :   Your Google OAuth2 Client Secret

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   Your Google OAuth2 Refresh Token

<a id="GmailCheckResult"></a>

`GmailCheckResult(**data: Any)`
:   Result of a health check operation.
    
    Returned by the check() method to indicate connectivity and credential status.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked_action: str | None`
    :   Action name used for the health check.

    `checked_entity: str | None`
    :   Entity name used for the health check.

    `error: str | None`
    :   Error message if status is 'unhealthy', None otherwise.

    `model_config`
    :   The type of the None singleton.

    `status: str`
    :   Health check status: 'healthy' or 'unhealthy'.

<a id="GmailExecuteResult"></a>

`GmailExecuteResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult[list[Label]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GmailExecuteResultWithMeta"></a>

`GmailExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta[list[DraftRef], DraftsListResultMeta]
    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta[list[MessageRef], MessagesListResultMeta]
    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta[list[ThreadRef], ThreadsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GmailExecuteResultWithMeta[list[DraftRef], DraftsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DraftsListResult"></a>

`DraftsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GmailExecuteResultWithMeta[list[MessageRef], MessagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MessagesListResult"></a>

`MessagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GmailExecuteResultWithMeta[list[ThreadRef], ThreadsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ThreadsListResult"></a>

`ThreadsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GmailExecuteResult[list[Label]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LabelsListResult"></a>

`LabelsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GmailReplicationConfig"></a>

`GmailReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Gmail.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `include_spam_and_trash: bool | None`
    :   Include messages from SPAM and TRASH in the results. Defaults to false.

    `model_config`
    :   The type of the None singleton.

<a id="Label"></a>

`Label(**data: Any)`
:   A Gmail label used to organize messages and threads
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `label_list_visibility: str | Any | None`
    :   The type of the None singleton.

    `message_list_visibility: str | Any | None`
    :   The type of the None singleton.

    `messages_total: int | Any | None`
    :   The type of the None singleton.

    `messages_unread: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `threads_total: int | Any | None`
    :   The type of the None singleton.

    `threads_unread: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="LabelColor"></a>

`LabelColor(**data: Any)`
:   The color to assign to a label
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background_color: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text_color: str | Any | None`
    :   The type of the None singleton.

<a id="LabelCreateParams"></a>

`LabelCreateParams(**data: Any)`
:   Parameters for creating a label
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: airbyte_agent_sdk.connectors.gmail.models.LabelCreateParamsColor | Any`
    :   The type of the None singleton.

    `label_list_visibility: str | Any`
    :   The type of the None singleton.

    `message_list_visibility: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="LabelCreateParamsColor"></a>

`LabelCreateParamsColor(**data: Any)`
:   The color to assign to the label
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background_color: str | Any`
    :   The background color of the label as a hex string (#RRGGBB)

    `model_config`
    :   The type of the None singleton.

    `text_color: str | Any`
    :   The text color of the label as a hex string (#RRGGBB)

<a id="LabelUpdateParams"></a>

`LabelUpdateParams(**data: Any)`
:   Parameters for updating a label
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: airbyte_agent_sdk.connectors.gmail.models.LabelUpdateParamsColor | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `label_list_visibility: str | Any`
    :   The type of the None singleton.

    `message_list_visibility: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="LabelUpdateParamsColor"></a>

`LabelUpdateParamsColor(**data: Any)`
:   The color to assign to the label
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background_color: str | Any`
    :   The background color of the label as a hex string (#RRGGBB)

    `model_config`
    :   The type of the None singleton.

    `text_color: str | Any`
    :   The text color of the label as a hex string (#RRGGBB)

<a id="LabelsListResponse"></a>

`LabelsListResponse(**data: Any)`
:   Response from listing labels
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `labels: list[airbyte_agent_sdk.connectors.gmail.models.Label] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Message"></a>

`Message(**data: Any)`
:   A Gmail email message
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `history_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `internal_date: str | Any | None`
    :   The type of the None singleton.

    `label_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `payload: Any`
    :   The type of the None singleton.

    `raw: str | Any | None`
    :   The type of the None singleton.

    `size_estimate: int | Any | None`
    :   The type of the None singleton.

    `snippet: str | Any | None`
    :   The type of the None singleton.

    `thread_id: str | Any | None`
    :   The type of the None singleton.

<a id="MessageHeader"></a>

`MessageHeader(**data: Any)`
:   A single email header key-value pair
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

<a id="MessageModifyParams"></a>

`MessageModifyParams(**data: Any)`
:   Parameters for modifying message labels
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `add_label_ids: list[str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `remove_label_ids: list[str] | Any`
    :   The type of the None singleton.

<a id="MessagePart"></a>

`MessagePart(**data: Any)`
:   A single MIME message part
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: Any`
    :   The type of the None singleton.

    `filename: str | Any | None`
    :   The type of the None singleton.

    `headers: list[airbyte_agent_sdk.connectors.gmail.models.MessageHeader] | Any | None`
    :   The type of the None singleton.

    `mime_type: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `part_id: str | Any | None`
    :   The type of the None singleton.

    `parts: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

<a id="MessagePartBody"></a>

`MessagePartBody(**data: Any)`
:   The body data of a MIME message part
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachment_id: str | Any | None`
    :   The type of the None singleton.

    `data: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `size: int | Any | None`
    :   The type of the None singleton.

<a id="MessageRef"></a>

`MessageRef(**data: Any)`
:   A lightweight reference to a message (used in list responses)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `thread_id: str | Any | None`
    :   The type of the None singleton.

<a id="MessageSendParams"></a>

`MessageSendParams(**data: Any)`
:   Parameters for sending a message
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `raw: str | Any`
    :   The type of the None singleton.

    `thread_id: str | Any`
    :   The type of the None singleton.

<a id="MessagesListResponse"></a>

`MessagesListResponse(**data: Any)`
:   Response from listing messages
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `messages: list[airbyte_agent_sdk.connectors.gmail.models.MessageRef] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any | None`
    :   The type of the None singleton.

    `result_size_estimate: int | Any | None`
    :   The type of the None singleton.

<a id="MessagesListResultMeta"></a>

`MessagesListResultMeta(**data: Any)`
:   Metadata for messages.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any | None`
    :   The type of the None singleton.

    `result_size_estimate: int | Any | None`
    :   The type of the None singleton.

<a id="Profile"></a>

`Profile(**data: Any)`
:   Gmail user profile information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email_address: str | Any | None`
    :   The type of the None singleton.

    `history_id: str | Any | None`
    :   The type of the None singleton.

    `messages_total: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `threads_total: int | Any | None`
    :   The type of the None singleton.

<a id="Thread"></a>

`Thread(**data: Any)`
:   A Gmail thread (email conversation)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `history_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `messages: list[airbyte_agent_sdk.connectors.gmail.models.Message] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `snippet: str | Any | None`
    :   The type of the None singleton.

<a id="ThreadRef"></a>

`ThreadRef(**data: Any)`
:   A lightweight reference to a thread (used in list responses)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `history_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `snippet: str | Any | None`
    :   The type of the None singleton.

<a id="ThreadsListResponse"></a>

`ThreadsListResponse(**data: Any)`
:   Response from listing threads
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any | None`
    :   The type of the None singleton.

    `result_size_estimate: int | Any | None`
    :   The type of the None singleton.

    `threads: list[airbyte_agent_sdk.connectors.gmail.models.ThreadRef] | Any`
    :   The type of the None singleton.

<a id="ThreadsListResultMeta"></a>

`ThreadsListResultMeta(**data: Any)`
:   Metadata for threads.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any | None`
    :   The type of the None singleton.

    `result_size_estimate: int | Any | None`
    :   The type of the None singleton.