---
id: airbyte_agent_sdk-connectors-gmail-types
title: airbyte_agent_sdk.connectors.gmail.types
---

Module airbyte_agent_sdk.connectors.gmail.types
===============================================
Type definitions for gmail connector.

Classes
-------

`DraftsCreateParams(*args, **kwargs)`
:   Parameters for drafts.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `message: airbyte_agent_sdk.connectors.gmail.types.DraftsCreateParamsMessage`
    :   The type of the None singleton.

`DraftsCreateParamsMessage(*args, **kwargs)`
:   The draft message content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `raw: str`
    :   The type of the None singleton.

    `threadId: str`
    :   The type of the None singleton.

`DraftsDeleteParams(*args, **kwargs)`
:   Parameters for drafts.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `draft_id: str`
    :   The type of the None singleton.

`DraftsGetParams(*args, **kwargs)`
:   Parameters for drafts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `draft_id: str`
    :   The type of the None singleton.

    `format: str`
    :   The type of the None singleton.

`DraftsListParams(*args, **kwargs)`
:   Parameters for drafts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include_spam_trash: bool`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

`DraftsSendCreateParams(*args, **kwargs)`
:   Parameters for drafts_send.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`DraftsUpdateParams(*args, **kwargs)`
:   Parameters for drafts.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `draft_id: str`
    :   The type of the None singleton.

    `message: airbyte_agent_sdk.connectors.gmail.types.DraftsUpdateParamsMessage`
    :   The type of the None singleton.

`DraftsUpdateParamsMessage(*args, **kwargs)`
:   The draft message content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `raw: str`
    :   The type of the None singleton.

    `threadId: str`
    :   The type of the None singleton.

`LabelsCreateParams(*args, **kwargs)`
:   Parameters for labels.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: airbyte_agent_sdk.connectors.gmail.types.LabelsCreateParamsColor`
    :   The type of the None singleton.

    `label_list_visibility: str`
    :   The type of the None singleton.

    `message_list_visibility: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

`LabelsCreateParamsColor(*args, **kwargs)`
:   The color to assign to the label

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `backgroundColor: str`
    :   The type of the None singleton.

    `textColor: str`
    :   The type of the None singleton.

`LabelsDeleteParams(*args, **kwargs)`
:   Parameters for labels.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `label_id: str`
    :   The type of the None singleton.

`LabelsGetParams(*args, **kwargs)`
:   Parameters for labels.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `label_id: str`
    :   The type of the None singleton.

`LabelsListParams(*args, **kwargs)`
:   Parameters for labels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`LabelsUpdateParams(*args, **kwargs)`
:   Parameters for labels.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: airbyte_agent_sdk.connectors.gmail.types.LabelsUpdateParamsColor`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `label_id: str`
    :   The type of the None singleton.

    `label_list_visibility: str`
    :   The type of the None singleton.

    `message_list_visibility: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

`LabelsUpdateParamsColor(*args, **kwargs)`
:   The color to assign to the label

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `backgroundColor: str`
    :   The type of the None singleton.

    `textColor: str`
    :   The type of the None singleton.

`MessagesCreateParams(*args, **kwargs)`
:   Parameters for messages.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `raw: str`
    :   The type of the None singleton.

    `thread_id: str`
    :   The type of the None singleton.

`MessagesGetParams(*args, **kwargs)`
:   Parameters for messages.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `format: str`
    :   The type of the None singleton.

    `message_id: str`
    :   The type of the None singleton.

    `metadata_headers: str`
    :   The type of the None singleton.

`MessagesListParams(*args, **kwargs)`
:   Parameters for messages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include_spam_trash: bool`
    :   The type of the None singleton.

    `label_ids: str`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

`MessagesTrashCreateParams(*args, **kwargs)`
:   Parameters for messages_trash.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `message_id: str`
    :   The type of the None singleton.

`MessagesUntrashCreateParams(*args, **kwargs)`
:   Parameters for messages_untrash.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `message_id: str`
    :   The type of the None singleton.

`MessagesUpdateParams(*args, **kwargs)`
:   Parameters for messages.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `add_label_ids: list[str]`
    :   The type of the None singleton.

    `message_id: str`
    :   The type of the None singleton.

    `remove_label_ids: list[str]`
    :   The type of the None singleton.

`ProfileGetParams(*args, **kwargs)`
:   Parameters for profile.get operation

    ### Ancestors (in MRO)

    * builtins.dict

`ThreadsGetParams(*args, **kwargs)`
:   Parameters for threads.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `format: str`
    :   The type of the None singleton.

    `metadata_headers: str`
    :   The type of the None singleton.

    `thread_id: str`
    :   The type of the None singleton.

`ThreadsListParams(*args, **kwargs)`
:   Parameters for threads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include_spam_trash: bool`
    :   The type of the None singleton.

    `label_ids: str`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.