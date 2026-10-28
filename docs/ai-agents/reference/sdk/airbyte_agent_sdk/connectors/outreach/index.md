---
id: airbyte_agent_sdk-connectors-outreach-index
title: airbyte_agent_sdk.connectors.outreach.index
---

Module airbyte_agent_sdk.connectors.outreach
============================================
Outreach connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* [airbyte_agent_sdk.connectors.outreach.connector](/ai-agents/reference/sdk/airbyte_agent_sdk/connectors/outreach/airbyte_agent_sdk-connectors-outreach-connector)
* [airbyte_agent_sdk.connectors.outreach.connector_model](/ai-agents/reference/sdk/airbyte_agent_sdk/connectors/outreach/airbyte_agent_sdk-connectors-outreach-connector_model)
* [airbyte_agent_sdk.connectors.outreach.models](/ai-agents/reference/sdk/airbyte_agent_sdk/connectors/outreach/airbyte_agent_sdk-connectors-outreach-models)
* [airbyte_agent_sdk.connectors.outreach.types](/ai-agents/reference/sdk/airbyte_agent_sdk/connectors/outreach/airbyte_agent_sdk-connectors-outreach-types)

Classes
-------

<a id="AccountsSearchData"></a>

`AccountsSearchData(**data: Any)`
:   Search result data for accounts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assigned_teams: list[typing.Any] | None`
    :   Assigned teams

    `assigned_users: list[typing.Any] | None`
    :   Assigned users

    `batches: list[typing.Any] | None`
    :   Batches

    `buyer_intent_score: float | None`
    :   Buyer intent score

    `company_type: str | None`
    :   Company type

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `custom1: str | None`
    :   Custom field 1

    `custom10: str | None`
    :   Custom field 10

    `custom100: str | None`
    :   Custom field 100

    `custom101: str | None`
    :   Custom field 101

    `custom102: str | None`
    :   Custom field 102

    `custom103: str | None`
    :   Custom field 103

    `custom104: str | None`
    :   Custom field 104

    `custom105: str | None`
    :   Custom field 105

    `custom106: str | None`
    :   Custom field 106

    `custom107: str | None`
    :   Custom field 107

    `custom108: str | None`
    :   Custom field 108

    `custom109: str | None`
    :   Custom field 109

    `custom11: str | None`
    :   Custom field 11

    `custom110: str | None`
    :   Custom field 110

    `custom111: str | None`
    :   Custom field 111

    `custom112: str | None`
    :   Custom field 112

    `custom113: str | None`
    :   Custom field 113

    `custom114: str | None`
    :   Custom field 114

    `custom115: str | None`
    :   Custom field 115

    `custom116: str | None`
    :   Custom field 116

    `custom117: str | None`
    :   Custom field 117

    `custom118: str | None`
    :   Custom field 118

    `custom119: str | None`
    :   Custom field 119

    `custom12: str | None`
    :   Custom field 12

    `custom120: str | None`
    :   Custom field 120

    `custom121: str | None`
    :   Custom field 121

    `custom122: str | None`
    :   Custom field 122

    `custom123: str | None`
    :   Custom field 123

    `custom124: str | None`
    :   Custom field 124

    `custom125: str | None`
    :   Custom field 125

    `custom126: str | None`
    :   Custom field 126

    `custom127: str | None`
    :   Custom field 127

    `custom128: str | None`
    :   Custom field 128

    `custom129: str | None`
    :   Custom field 129

    `custom13: str | None`
    :   Custom field 13

    `custom130: str | None`
    :   Custom field 130

    `custom131: str | None`
    :   Custom field 131

    `custom132: str | None`
    :   Custom field 132

    `custom133: str | None`
    :   Custom field 133

    `custom134: str | None`
    :   Custom field 134

    `custom135: str | None`
    :   Custom field 135

    `custom136: str | None`
    :   Custom field 136

    `custom137: str | None`
    :   Custom field 137

    `custom138: str | None`
    :   Custom field 138

    `custom139: str | None`
    :   Custom field 139

    `custom14: str | None`
    :   Custom field 14

    `custom140: str | None`
    :   Custom field 140

    `custom141: str | None`
    :   Custom field 141

    `custom142: str | None`
    :   Custom field 142

    `custom143: str | None`
    :   Custom field 143

    `custom144: str | None`
    :   Custom field 144

    `custom145: str | None`
    :   Custom field 145

    `custom146: str | None`
    :   Custom field 146

    `custom147: str | None`
    :   Custom field 147

    `custom148: str | None`
    :   Custom field 148

    `custom149: str | None`
    :   Custom field 149

    `custom15: str | None`
    :   Custom field 15

    `custom150: str | None`
    :   Custom field 150

    `custom16: str | None`
    :   Custom field 16

    `custom17: str | None`
    :   Custom field 17

    `custom18: str | None`
    :   Custom field 18

    `custom19: str | None`
    :   Custom field 19

    `custom2: str | None`
    :   Custom field 2

    `custom20: str | None`
    :   Custom field 20

    `custom21: str | None`
    :   Custom field 21

    `custom22: str | None`
    :   Custom field 22

    `custom23: str | None`
    :   Custom field 23

    `custom24: str | None`
    :   Custom field 24

    `custom25: str | None`
    :   Custom field 25

    `custom26: str | None`
    :   Custom field 26

    `custom27: str | None`
    :   Custom field 27

    `custom28: str | None`
    :   Custom field 28

    `custom29: str | None`
    :   Custom field 29

    `custom3: str | None`
    :   Custom field 3

    `custom30: str | None`
    :   Custom field 30

    `custom31: str | None`
    :   Custom field 31

    `custom32: str | None`
    :   Custom field 32

    `custom33: str | None`
    :   Custom field 33

    `custom34: str | None`
    :   Custom field 34

    `custom35: str | None`
    :   Custom field 35

    `custom36: str | None`
    :   Custom field 36

    `custom37: str | None`
    :   Custom field 37

    `custom38: str | None`
    :   Custom field 38

    `custom39: str | None`
    :   Custom field 39

    `custom4: str | None`
    :   Custom field 4

    `custom40: str | None`
    :   Custom field 40

    `custom41: str | None`
    :   Custom field 41

    `custom42: str | None`
    :   Custom field 42

    `custom43: str | None`
    :   Custom field 43

    `custom44: str | None`
    :   Custom field 44

    `custom45: str | None`
    :   Custom field 45

    `custom46: str | None`
    :   Custom field 46

    `custom47: str | None`
    :   Custom field 47

    `custom48: str | None`
    :   Custom field 48

    `custom49: str | None`
    :   Custom field 49

    `custom5: str | None`
    :   Custom field 5

    `custom50: str | None`
    :   Custom field 50

    `custom51: str | None`
    :   Custom field 51

    `custom52: str | None`
    :   Custom field 52

    `custom53: str | None`
    :   Custom field 53

    `custom54: str | None`
    :   Custom field 54

    `custom55: str | None`
    :   Custom field 55

    `custom56: str | None`
    :   Custom field 56

    `custom57: str | None`
    :   Custom field 57

    `custom58: str | None`
    :   Custom field 58

    `custom59: str | None`
    :   Custom field 59

    `custom6: str | None`
    :   Custom field 6

    `custom60: str | None`
    :   Custom field 60

    `custom61: str | None`
    :   Custom field 61

    `custom62: str | None`
    :   Custom field 62

    `custom63: str | None`
    :   Custom field 63

    `custom64: str | None`
    :   Custom field 64

    `custom65: str | None`
    :   Custom field 65

    `custom66: str | None`
    :   Custom field 66

    `custom67: str | None`
    :   Custom field 67

    `custom68: str | None`
    :   Custom field 68

    `custom69: str | None`
    :   Custom field 69

    `custom7: str | None`
    :   Custom field 7

    `custom70: str | None`
    :   Custom field 70

    `custom71: str | None`
    :   Custom field 71

    `custom72: str | None`
    :   Custom field 72

    `custom73: str | None`
    :   Custom field 73

    `custom74: str | None`
    :   Custom field 74

    `custom75: str | None`
    :   Custom field 75

    `custom76: str | None`
    :   Custom field 76

    `custom77: str | None`
    :   Custom field 77

    `custom78: str | None`
    :   Custom field 78

    `custom79: str | None`
    :   Custom field 79

    `custom8: str | None`
    :   Custom field 8

    `custom80: str | None`
    :   Custom field 80

    `custom81: str | None`
    :   Custom field 81

    `custom82: str | None`
    :   Custom field 82

    `custom83: str | None`
    :   Custom field 83

    `custom84: str | None`
    :   Custom field 84

    `custom85: str | None`
    :   Custom field 85

    `custom86: str | None`
    :   Custom field 86

    `custom87: str | None`
    :   Custom field 87

    `custom88: str | None`
    :   Custom field 88

    `custom89: str | None`
    :   Custom field 89

    `custom9: str | None`
    :   Custom field 9

    `custom90: str | None`
    :   Custom field 90

    `custom91: str | None`
    :   Custom field 91

    `custom92: str | None`
    :   Custom field 92

    `custom93: str | None`
    :   Custom field 93

    `custom94: str | None`
    :   Custom field 94

    `custom95: str | None`
    :   Custom field 95

    `custom96: str | None`
    :   Custom field 96

    `custom97: str | None`
    :   Custom field 97

    `custom98: str | None`
    :   Custom field 98

    `custom99: str | None`
    :   Custom field 99

    `custom_id: str | None`
    :   Custom id

    `default_plugin_mapping: list[typing.Any] | None`
    :   Default plugin mapping

    `description: str | None`
    :   Description

    `domain: str | None`
    :   Domain

    `external_source: str | None`
    :   External source

    `favorites: list[typing.Any] | None`
    :   Favorites

    `followers: int | None`
    :   Followers

    `founded_at: str | None`
    :   Founded at

    `id: int | None`
    :   Unique account identifier

    `industry: str | None`
    :   Industry

    `linked_in_employees: int | None`
    :   Linked in employees

    `linked_in_url: str | None`
    :   Linked in url

    `locality: str | None`
    :   Locality

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `named: bool | None`
    :   Named

    `natural_name: str | None`
    :   Natural name

    `number_of_employees: int | None`
    :   Number of employees

    `owner: list[typing.Any] | None`
    :   Owner

    `prospects: list[typing.Any] | None`
    :   Prospects

    `sharing_team_id: str | None`
    :   Sharing team id

    `tags: list[typing.Any] | None`
    :   Tags

    `tasks: list[typing.Any] | None`
    :   Tasks

    `touched_at: str | None`
    :   Touched at

    `trashed_at: str | None`
    :   Trashed at

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

    `website_url: str | None`
    :   Website url

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

<a id="AirbyteSearchMeta"></a>

`AirbyteSearchMeta(**data: Any)`
:   Pagination metadata for search responses.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   Cursor for fetching the next page of results.

    `has_more: bool`
    :   Whether more results are available.

    `model_config`
    :   The type of the None singleton.

    `took_ms: int | None`
    :   Time taken to execute the search in milliseconds.

<a id="AirbyteSearchResult"></a>

`AirbyteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[AccountsSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[CallDispositionsSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[CallPurposesSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[CallsSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[MailboxesSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[MailingsSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[OpportunitiesSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[PersonasSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[ProspectsSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[SequenceStatesSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[SequenceStepsSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[SequencesSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[SnippetsSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[StagesSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[TasksSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[TemplatesSearchData]
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AccountsSearchResult"></a>

`AccountsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallDispositionsSearchResult"></a>

`CallDispositionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallPurposesSearchResult"></a>

`CallPurposesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallsSearchResult"></a>

`CallsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MailboxesSearchResult"></a>

`MailboxesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MailingsSearchResult"></a>

`MailingsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OpportunitiesSearchResult"></a>

`OpportunitiesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="PersonasSearchResult"></a>

`PersonasSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ProspectsSearchResult"></a>

`ProspectsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SequenceStatesSearchResult"></a>

`SequenceStatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SequenceStepsSearchResult"></a>

`SequenceStepsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SequencesSearchResult"></a>

`SequencesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SnippetsSearchResult"></a>

`SnippetsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="StagesSearchResult"></a>

`StagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TasksSearchResult"></a>

`TasksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TemplatesSearchResult"></a>

`TemplatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="UsersSearchResult"></a>

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallDispositionsSearchData"></a>

`CallDispositionsSearchData(**data: Any)`
:   Search result data for call_dispositions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls: list[typing.Any] | None`
    :   Calls

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `default_for_outbound_voicemail: bool | None`
    :   Default for outbound voicemail

    `id: int | None`
    :   Unique call disposition identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `order: int | None`
    :   Order

    `outcome: str | None`
    :   Outcome

    `updated_at: str | None`
    :   Updated at

<a id="CallPurposesSearchData"></a>

`CallPurposesSearchData(**data: Any)`
:   Search result data for call_purposes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls: list[typing.Any] | None`
    :   Calls

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `id: int | None`
    :   Unique call purpose identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `order: int | None`
    :   Order

    `updated_at: str | None`
    :   Updated at

<a id="CallsSearchData"></a>

`CallsSearchData(**data: Any)`
:   Search result data for calls entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answered_at: str | None`
    :   Answered at

    `batches: list[typing.Any] | None`
    :   Batches

    `call_disposition: list[typing.Any] | None`
    :   Call disposition

    `call_purpose: list[typing.Any] | None`
    :   Call purpose

    `completed_at: str | None`
    :   Completed at

    `created_at: str | None`
    :   Created at

    `dialed_at: str | None`
    :   Dialed at

    `direction: str | None`
    :   Direction

    `external_vendor: str | None`
    :   External vendor

    `from_: str | None`
    :   From

    `id: int | None`
    :   Unique call identifier

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Note

    `opportunity: list[typing.Any] | None`
    :   Opportunity

    `outbound_voicemail: list[typing.Any] | None`
    :   Outbound voicemail

    `outcome: str | None`
    :   Outcome

    `phone: list[typing.Any] | None`
    :   Phone

    `phone_number: list[typing.Any] | None`
    :   Phone number

    `prospect: list[typing.Any] | None`
    :   Prospect

    `recording_deletion_reason: str | None`
    :   Recording deletion reason

    `recording_url: str | None`
    :   Recording url

    `returned_at: str | None`
    :   Returned at

    `sequence: list[typing.Any] | None`
    :   Sequence

    `sequence_action: str | None`
    :   Sequence action

    `sequence_state: list[typing.Any] | None`
    :   Sequence state

    `sequence_step: list[typing.Any] | None`
    :   Sequence step

    `should_record_call: bool | None`
    :   Should record call

    `state: str | None`
    :   State

    `state_changed_at: str | None`
    :   State changed at

    `tags: list[typing.Any] | None`
    :   Tags

    `task: list[typing.Any] | None`
    :   Task

    `to: str | None`
    :   To

    `uid: str | None`
    :   Uid

    `updated_at: str | None`
    :   Updated at

    `user: list[typing.Any] | None`
    :   User

    `user_call_type: str | None`
    :   User call type

    `vendor_call_id: str | None`
    :   Vendor call id

    `voicemail_recording_url: str | None`
    :   Voicemail recording url

<a id="MailboxesSearchData"></a>

`MailboxesSearchData(**data: Any)`
:   Search result data for mailboxes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auth_id: int | None`
    :   Auth id

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `editable: bool | None`
    :   Editable

    `email: str | None`
    :   Email

    `email_hash: str | None`
    :   Email hash

    `email_provider: str | None`
    :   Email provider

    `email_signature: str | None`
    :   Email signature

    `ews_custom_search_folder: bool | None`
    :   Ews custom search folder

    `ews_delegate_sync: bool | None`
    :   Ews delegate sync

    `ews_endpoint: str | None`
    :   Ews endpoint

    `ews_impersonation: bool | None`
    :   Ews impersonation

    `ews_ssl_verify_mode: int | None`
    :   Ews ssl verify mode

    `exchange_version: str | None`
    :   Exchange version

    `id: int | None`
    :   Unique mailbox identifier

    `imap_host: str | None`
    :   Imap host

    `imap_port: int | None`
    :   Imap port

    `imap_ssl: bool | None`
    :   Imap ssl

    `mail_aliases: list[typing.Any] | None`
    :   Mail aliases

    `mailings: list[typing.Any] | None`
    :   Mailings

    `max_emails_per_day: int | None`
    :   Max emails per day

    `max_mailings_per_day: int | None`
    :   Max mailings per day

    `max_mailings_per_week: int | None`
    :   Max mailings per week

    `model_config`
    :   The type of the None singleton.

    `opt_out_message: str | None`
    :   Opt out message

    `opt_out_signature: str | None`
    :   Opt out signature

    `prospect_email_exclusions: list[typing.Any] | None`
    :   Prospect email exclusions

    `provider_id: int | None`
    :   Provider id

    `provider_type: str | None`
    :   Provider type

    `send_disabled: bool | None`
    :   Send disabled

    `send_errored_at: str | None`
    :   Send errored at

    `send_max_retries: int | None`
    :   Send max retries

    `send_method: str | None`
    :   Send method

    `send_period: int | None`
    :   Send period

    `send_permanent_error_at: str | None`
    :   Send permanent error at

    `send_requires_sync: bool | None`
    :   Send requires sync

    `send_success_at: str | None`
    :   Send success at

    `send_threshold: int | None`
    :   Send threshold

    `sendgrid_webhook_url: str | None`
    :   Sendgrid webhook url

    `smtp_host: str | None`
    :   Smtp host

    `smtp_port: int | None`
    :   Smtp port

    `smtp_ssl: bool | None`
    :   Smtp ssl

    `smtp_username: str | None`
    :   Smtp username

    `sync_active_frequency: int | None`
    :   Sync active frequency

    `sync_disabled: bool | None`
    :   Sync disabled

    `sync_errored_at: str | None`
    :   Sync errored at

    `sync_finished_at: str | None`
    :   Sync finished at

    `sync_method: str | None`
    :   Sync method

    `sync_outreach_folder: bool | None`
    :   Sync outreach folder

    `sync_passive_frequency: int | None`
    :   Sync passive frequency

    `sync_permanent_error_at: str | None`
    :   Sync permanent error at

    `sync_success_at: str | None`
    :   Sync success at

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

    `user: list[typing.Any] | None`
    :   User

    `user_id: int | None`
    :   User id

    `username: str | None`
    :   Username

<a id="MailingsSearchData"></a>

`MailingsSearchData(**data: Any)`
:   Search result data for mailings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachments: list[typing.Any] | None`
    :   Attachments

    `attributable_sequence_id: int | None`
    :   Attributable sequence id

    `attributable_sequence_name: str | None`
    :   Attributable sequence name

    `body_html: str | None`
    :   Body html

    `body_text: str | None`
    :   Body text

    `bounced_at: str | None`
    :   Bounced at

    `calendar: list[typing.Any] | None`
    :   Calendar

    `click_count: int | None`
    :   Click count

    `clicked_at: str | None`
    :   Clicked at

    `created_at: str | None`
    :   Created at

    `delivered_at: str | None`
    :   Delivered at

    `desired_at: str | None`
    :   Desired at

    `error_backtrace: str | None`
    :   Error backtrace

    `error_reason: str | None`
    :   Error reason

    `follow_up_sequence: list[typing.Any] | None`
    :   Follow up sequence

    `follow_up_sequence_id: int | None`
    :   Follow up sequence id

    `follow_up_sequence_name: str | None`
    :   Follow up sequence name

    `follow_up_sequence_starting_date: str | None`
    :   Follow up sequence starting date

    `follow_up_task_scheduled_at: str | None`
    :   Follow up task scheduled at

    `follow_up_task_type: str | None`
    :   Follow up task type

    `id: int | None`
    :   Unique mailing identifier

    `mailbox: list[typing.Any] | None`
    :   Mailbox

    `mailbox_address: str | None`
    :   Mailbox address

    `mailing_type: str | None`
    :   Mailing type

    `marked_as_spam_at: str | None`
    :   Marked as spam at

    `meeting_description: str | None`
    :   Meeting description

    `meeting_duration: int | None`
    :   Meeting duration

    `meeting_location: str | None`
    :   Meeting location

    `meeting_title: str | None`
    :   Meeting title

    `message_id: str | None`
    :   Message id

    `model_config`
    :   The type of the None singleton.

    `notify_thread_condition: str | None`
    :   Notify thread condition

    `notify_thread_scheduled_at: str | None`
    :   Notify thread scheduled at

    `notify_thread_status: str | None`
    :   Notify thread status

    `open_count: int | None`
    :   Open count

    `opened_at: str | None`
    :   Opened at

    `opportunity: list[typing.Any] | None`
    :   Opportunity

    `optimized_scheduled_at: str | None`
    :   Optimized scheduled at

    `override_safety_settings: bool | None`
    :   Override safety settings

    `prospect: list[typing.Any] | None`
    :   Prospect

    `recipients: list[typing.Any] | None`
    :   Recipients

    `references: list[typing.Any] | None`
    :   References

    `replied_at: str | None`
    :   Replied at

    `reply_sentiment: str | None`
    :   Reply sentiment

    `retry_at: str | None`
    :   Retry at

    `retry_count: int | None`
    :   Retry count

    `retry_interval: int | None`
    :   Retry interval

    `schedule: list[typing.Any] | None`
    :   Schedule

    `schedule_id: int | None`
    :   Schedule id

    `scheduled_at: str | None`
    :   Scheduled at

    `sequence: list[typing.Any] | None`
    :   Sequence

    `sequence_state: list[typing.Any] | None`
    :   Sequence state

    `sequence_step: list[typing.Any] | None`
    :   Sequence step

    `state: str | None`
    :   State

    `state_changed_at: str | None`
    :   State changed at

    `subject: str | None`
    :   Subject

    `task: list[typing.Any] | None`
    :   Task

    `tasks: list[typing.Any] | None`
    :   Tasks

    `template: list[typing.Any] | None`
    :   Template

    `track_links: bool | None`
    :   Track links

    `track_opens: bool | None`
    :   Track opens

    `unsubscribed_at: str | None`
    :   Unsubscribed at

    `updated_at: str | None`
    :   Updated at

    `user: list[typing.Any] | None`
    :   User

<a id="OpportunitiesSearchData"></a>

`OpportunitiesSearchData(**data: Any)`
:   Search result data for opportunities entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: list[typing.Any] | None`
    :   Account

    `amount: int | None`
    :   Amount

    `assigned_teams: list[typing.Any] | None`
    :   Assigned teams

    `assigned_users: list[typing.Any] | None`
    :   Assigned users

    `close_date: str | None`
    :   Close date

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `currency_type: str | None`
    :   Currency type

    `custom1: str | None`
    :   Custom field 1

    `custom10: str | None`
    :   Custom field 10

    `custom100: str | None`
    :   Custom field 100

    `custom101: str | None`
    :   Custom field 101

    `custom102: str | None`
    :   Custom field 102

    `custom103: str | None`
    :   Custom field 103

    `custom104: str | None`
    :   Custom field 104

    `custom105: str | None`
    :   Custom field 105

    `custom106: str | None`
    :   Custom field 106

    `custom107: str | None`
    :   Custom field 107

    `custom108: str | None`
    :   Custom field 108

    `custom109: str | None`
    :   Custom field 109

    `custom11: str | None`
    :   Custom field 11

    `custom110: str | None`
    :   Custom field 110

    `custom111: str | None`
    :   Custom field 111

    `custom112: str | None`
    :   Custom field 112

    `custom113: str | None`
    :   Custom field 113

    `custom114: str | None`
    :   Custom field 114

    `custom115: str | None`
    :   Custom field 115

    `custom116: str | None`
    :   Custom field 116

    `custom117: str | None`
    :   Custom field 117

    `custom118: str | None`
    :   Custom field 118

    `custom119: str | None`
    :   Custom field 119

    `custom12: str | None`
    :   Custom field 12

    `custom120: str | None`
    :   Custom field 120

    `custom121: str | None`
    :   Custom field 121

    `custom122: str | None`
    :   Custom field 122

    `custom123: str | None`
    :   Custom field 123

    `custom124: str | None`
    :   Custom field 124

    `custom125: str | None`
    :   Custom field 125

    `custom126: str | None`
    :   Custom field 126

    `custom127: str | None`
    :   Custom field 127

    `custom128: str | None`
    :   Custom field 128

    `custom129: str | None`
    :   Custom field 129

    `custom13: str | None`
    :   Custom field 13

    `custom130: str | None`
    :   Custom field 130

    `custom131: str | None`
    :   Custom field 131

    `custom132: str | None`
    :   Custom field 132

    `custom133: str | None`
    :   Custom field 133

    `custom134: str | None`
    :   Custom field 134

    `custom135: str | None`
    :   Custom field 135

    `custom136: str | None`
    :   Custom field 136

    `custom137: str | None`
    :   Custom field 137

    `custom138: str | None`
    :   Custom field 138

    `custom139: str | None`
    :   Custom field 139

    `custom14: str | None`
    :   Custom field 14

    `custom140: str | None`
    :   Custom field 140

    `custom141: str | None`
    :   Custom field 141

    `custom142: str | None`
    :   Custom field 142

    `custom143: str | None`
    :   Custom field 143

    `custom144: str | None`
    :   Custom field 144

    `custom145: str | None`
    :   Custom field 145

    `custom146: str | None`
    :   Custom field 146

    `custom147: str | None`
    :   Custom field 147

    `custom148: str | None`
    :   Custom field 148

    `custom149: str | None`
    :   Custom field 149

    `custom15: str | None`
    :   Custom field 15

    `custom150: str | None`
    :   Custom field 150

    `custom16: str | None`
    :   Custom field 16

    `custom17: str | None`
    :   Custom field 17

    `custom18: str | None`
    :   Custom field 18

    `custom19: str | None`
    :   Custom field 19

    `custom2: str | None`
    :   Custom field 2

    `custom20: str | None`
    :   Custom field 20

    `custom21: str | None`
    :   Custom field 21

    `custom22: str | None`
    :   Custom field 22

    `custom23: str | None`
    :   Custom field 23

    `custom24: str | None`
    :   Custom field 24

    `custom25: str | None`
    :   Custom field 25

    `custom26: str | None`
    :   Custom field 26

    `custom27: str | None`
    :   Custom field 27

    `custom28: str | None`
    :   Custom field 28

    `custom29: str | None`
    :   Custom field 29

    `custom3: str | None`
    :   Custom field 3

    `custom30: str | None`
    :   Custom field 30

    `custom31: str | None`
    :   Custom field 31

    `custom32: str | None`
    :   Custom field 32

    `custom33: str | None`
    :   Custom field 33

    `custom34: str | None`
    :   Custom field 34

    `custom35: str | None`
    :   Custom field 35

    `custom36: str | None`
    :   Custom field 36

    `custom37: str | None`
    :   Custom field 37

    `custom38: str | None`
    :   Custom field 38

    `custom39: str | None`
    :   Custom field 39

    `custom4: str | None`
    :   Custom field 4

    `custom40: str | None`
    :   Custom field 40

    `custom41: str | None`
    :   Custom field 41

    `custom42: str | None`
    :   Custom field 42

    `custom43: str | None`
    :   Custom field 43

    `custom44: str | None`
    :   Custom field 44

    `custom45: str | None`
    :   Custom field 45

    `custom46: str | None`
    :   Custom field 46

    `custom47: str | None`
    :   Custom field 47

    `custom48: str | None`
    :   Custom field 48

    `custom49: str | None`
    :   Custom field 49

    `custom5: str | None`
    :   Custom field 5

    `custom50: str | None`
    :   Custom field 50

    `custom51: str | None`
    :   Custom field 51

    `custom52: str | None`
    :   Custom field 52

    `custom53: str | None`
    :   Custom field 53

    `custom54: str | None`
    :   Custom field 54

    `custom55: str | None`
    :   Custom field 55

    `custom56: str | None`
    :   Custom field 56

    `custom57: str | None`
    :   Custom field 57

    `custom58: str | None`
    :   Custom field 58

    `custom59: str | None`
    :   Custom field 59

    `custom6: str | None`
    :   Custom field 6

    `custom60: str | None`
    :   Custom field 60

    `custom61: str | None`
    :   Custom field 61

    `custom62: str | None`
    :   Custom field 62

    `custom63: str | None`
    :   Custom field 63

    `custom64: str | None`
    :   Custom field 64

    `custom65: str | None`
    :   Custom field 65

    `custom66: str | None`
    :   Custom field 66

    `custom67: str | None`
    :   Custom field 67

    `custom68: str | None`
    :   Custom field 68

    `custom69: str | None`
    :   Custom field 69

    `custom7: str | None`
    :   Custom field 7

    `custom70: str | None`
    :   Custom field 70

    `custom71: str | None`
    :   Custom field 71

    `custom72: str | None`
    :   Custom field 72

    `custom73: str | None`
    :   Custom field 73

    `custom74: str | None`
    :   Custom field 74

    `custom75: str | None`
    :   Custom field 75

    `custom76: str | None`
    :   Custom field 76

    `custom77: str | None`
    :   Custom field 77

    `custom78: str | None`
    :   Custom field 78

    `custom79: str | None`
    :   Custom field 79

    `custom8: str | None`
    :   Custom field 8

    `custom80: str | None`
    :   Custom field 80

    `custom81: str | None`
    :   Custom field 81

    `custom82: str | None`
    :   Custom field 82

    `custom83: str | None`
    :   Custom field 83

    `custom84: str | None`
    :   Custom field 84

    `custom85: str | None`
    :   Custom field 85

    `custom86: str | None`
    :   Custom field 86

    `custom87: str | None`
    :   Custom field 87

    `custom88: str | None`
    :   Custom field 88

    `custom89: str | None`
    :   Custom field 89

    `custom9: str | None`
    :   Custom field 9

    `custom90: str | None`
    :   Custom field 90

    `custom91: str | None`
    :   Custom field 91

    `custom92: str | None`
    :   Custom field 92

    `custom93: str | None`
    :   Custom field 93

    `custom94: str | None`
    :   Custom field 94

    `custom95: str | None`
    :   Custom field 95

    `custom96: str | None`
    :   Custom field 96

    `custom97: str | None`
    :   Custom field 97

    `custom98: str | None`
    :   Custom field 98

    `custom99: str | None`
    :   Custom field 99

    `default_plugin_mapping: list[typing.Any] | None`
    :   Default plugin mapping

    `description: str | None`
    :   Description

    `external_created_at: str | None`
    :   External created at

    `external_creator: list[typing.Any] | None`
    :   External creator

    `favorites: list[typing.Any] | None`
    :   Favorites

    `health_category: str | None`
    :   Health category

    `health_score: int | None`
    :   Health score

    `id: int | None`
    :   Unique opportunity identifier

    `map_link: str | None`
    :   Map link

    `map_next_steps: str | None`
    :   Map next steps

    `map_number_of_overdue_tasks: int | None`
    :   Map number of overdue tasks

    `map_status: str | None`
    :   Map status

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `next_step: str | None`
    :   Next step

    `opportunity_health_factors: list[typing.Any] | None`
    :   Opportunity health factors

    `opportunity_stage: list[typing.Any] | None`
    :   Opportunity stage

    `opportunity_type: str | None`
    :   Opportunity type

    `owner: list[typing.Any] | None`
    :   Owner

    `primary_prospect: list[typing.Any] | None`
    :   Primary prospect

    `probability: int | None`
    :   Probability

    `prospecting_rep_id: str | None`
    :   Prospecting rep id

    `prospects: list[typing.Any] | None`
    :   Prospects

    `sharing_team_id: str | None`
    :   Sharing team id

    `stage: list[typing.Any] | None`
    :   Stage

    `tags: list[typing.Any] | None`
    :   Tags

    `touched_at: str | None`
    :   Touched at

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

<a id="OutreachAuthConfig"></a>

`OutreachAuthConfig(**data: Any)`
:   OAuth2 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   The Client ID of your Outreach developer application

    `client_secret: str`
    :   The Client Secret of your Outreach developer application

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   The token for obtaining the new access token

<a id="OutreachConnector"></a>

`OutreachConnector(auth_config: OutreachAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Outreach API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new outreach connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., OutreachAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = OutreachConnector(auth_config=OutreachAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = OutreachConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = OutreachConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )

    ### Class variables

    `connector_name`
    :   The type of the None singleton.

    `connector_version`
    :   The type of the None singleton.

    `sdk_version`
    :   The type of the None singleton.

    ### Static methods

    `agent_tool(role: AgentToolRole | None = None, *, inspect_tool: str | None = None, docs_tool: str | None = None, max_output_chars: int | None | Unset = UNSET, framework: FrameworkName = 'none', internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> Callable[[~_F], ~_F]`
    :   Decorator for new user-written connector tool functions.
        
        Use this when a tool needs a custom body or the framework lacks a
        native strategy. Instead of baking the full entity/action reference
        into the docstring, it instructs the agent to call this connector's
        inspect and docs tools before executing. Tool failures raise
        :class:`airbyte_agent_sdk.AirbyteToolError` by default
        (``framework="none"``, no auto-detection) — pass ``framework=...`` to
        translate to a supported framework's signal instead.
        
        Decorate three functions per connector — execute, inspect and docs.
        The role is inferred from each function's signature (extra parameters
        are allowed); a signature matching more than one role, a generic
        ``(*args, **kwargs)`` wrapper, or a callable whose signature cannot
        be read must pass the role explicitly:
        
        - ``(entity, action, ...)`` -> ``"execute"``
        - ``(section, ...)``        -> ``"read_skill_docs"``
        - ``()``                    -> ``"inspect_connector"``
        
        Usage:
            connector = OutreachConnector(...)
        
            @OutreachConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @OutreachConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @OutreachConnector.agent_tool()
            async def read_skill_docs(section: str | None = None):
                return await connector.read_skill_docs(section)
        
        Args:
            role: ``"execute" | "inspect_connector" | "read_skill_docs"``.
                None (default) infers the role from the decorated function's
                signature; an explicit role validates the canonical
                parameters are present (functions accepting ``**kwargs``, or
                callables whose signature cannot be read, pass validation).
            inspect_tool: Exact registered name of the sibling inspect tool,
                woven into the execute docstring for tighter steering.
                Defaults to generic phrasing.
            docs_tool: Exact registered name of the sibling docs tool (see
                inspect_tool).
            max_output_chars: Max serialized output size before failing.
                Defaults per role: execute -> DEFAULT_MAX_OUTPUT_CHARS, docs
                tools -> None.
            framework: Translation target for tool failures. Defaults to
                ``"none"`` (raise AirbyteToolError); never auto-detects.
            internal_retries: How many transient runtime failures (429/5xx,
                network, timeout) to retry silently before surfacing.
                Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs)
                -> bool`` further restricting which retryable errors are safe
                for this specific tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback ``(error,
                args, kwargs) -> str | None`` invoked after internal retries
                are exhausted or skipped. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Deprecated. Add connector-specific documentation and runtime safeguards to one tool.
        
        Kept for backwards compatibility with existing single-tool
        integrations; it is not removed and does not warn at runtime, but new
        code should use `build_connector_tools` or `agent_tool` below.
        
        For new agents, prefer `build_connector_tools`. It returns progressive
        `inspect_connector`, `read_skill_docs`, and `execute` tools so the agent
        can load only the connector guidance it needs:
        
        ```python
        from airbyte_agent_sdk import build_connector_tools
        from pydantic_ai import Agent
        
        tools = build_connector_tools(connector, framework="pydantic_ai")
        agent = Agent("openai:gpt-4o", tools=tools.as_list())
        ```
        
        When a new integration needs custom tool bodies or a framework
        without native support, use `agent_tool` instead.
        
        ### Legacy: one generated-description tool
        
        Existing integrations can keep using `tool_utils` for one broad
        `execute` tool with the connector's full generated catalog in its
        description:
        
        ```python
        from fastmcp import FastMCP
        
        connector = OutreachConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @OutreachConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @OutreachConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @OutreachConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        This decorator composes `translate_exceptions` for runtime wrapping,
        output-size checks, framework signal translation, and optional internal
        retries, then adds connector-specific docstring augmentation.
        
        Args:
            update_docstring: When True, append connector capabilities to `__doc__`.
            max_output_chars: Max serialized output size before raising. Use `None` to disable.
            framework: One of `"pydantic_ai" | "langchain" | "openai_agents" | "mcp" | "none"`.
                Defaults to `None`, which auto-detects each framework's canonical
                import in order and falls back to `"none"` with a warning when no
                supported framework is installed. Explicit always wins, and an
                explicit framework whose package is missing raises `RuntimeError`.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                `airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate `(error, args, kwargs) -> bool`
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                `(error, args, kwargs) -> str | None`. Invoked after internal retries
                are exhausted or were skipped because `should_internal_retry` returned
                `False`. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            OutreachCheckResult with status ("healthy" or "unhealthy") and optional error message
        
        Example:
            result = await connector.check()
            if result.status == "healthy":
                print("Connection verified!")
            else:
                print(f"Check failed: \{result.error\}")

    `close(self)`
    :   Close the connector and release resources.

    `entity_schema(self, entity: str) ‑> dict[str, typing.Any] | None`
    :   Get the JSON schema for an entity.
        
        Args:
            entity: Entity name (e.g., "contacts", "companies")
        
        Returns:
            JSON schema dict describing the entity structure, or None if not found.
        
        Example:
            schema = connector.entity_schema("contacts")
            if schema:
                print(f"Contact properties: \{list(schema.get('properties', \{\}).keys())\}")

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search', 'context_store_sql_query']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
            select_fields: Optional allowlist of dot-notation fields to include
            exclude_fields: Optional blocklist of dot-notation fields to remove
            skip_truncation: Disable long-text truncation for collection actions
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `inspect_connector(self) ‑> dict[str, typing.Any]`
    :   Inspect this connector's hosted metadata/readiness and resolve its docs skill id.
        
        Call this before read_skill_docs in the normal hosted flow. For
        local/offline connectors this returns a local-mode payload with a
        warning instead of a hosted inspection.
        
        Example:
            info = await connector.inspect_connector()
            print(info["docs_skill_id"])

    `list_entities(self) ‑> list[dict[str, typing.Any]]`
    :   Get structured data about available entities, actions, and parameters.
        
        Returns a list of entity descriptions with:
        - entity_name: Name of the entity (e.g., "contacts", "deals")
        - description: Entity description from the first endpoint
        - available_actions: List of actions (e.g., ["list", "get", "create"])
        - parameters: Dict mapping action -> list of parameter dicts
        
        Example:
            entities = connector.list_entities()
            for entity in entities:
                print(f"\{entity['entity_name']\}: \{entity['available_actions']\}")

    `read_skill_docs(self, section: str | None = None) ‑> str`
    :   Read this connector's usage docs, rendered to text.
        
        Omit section for the outline and general guidance; pass an exact
        section id from the outline for full details. For local/offline
        connectors the full generated docs are returned and section is
        ignored.
        
        Example:
            outline = await connector.read_skill_docs()
            details = await connector.read_skill_docs(section="entity:contacts")

<a id="OutreachReplicationConfig"></a>

`OutreachReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Outreach.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   The date from which you'd like to replicate data for Outreach API, in the format YYYY-MM-DDT00:00:00Z.

<a id="PersonasSearchData"></a>

`PersonasSearchData(**data: Any)`
:   Search result data for personas entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Created at

    `description: str | None`
    :   Description

    `id: int | None`
    :   Unique persona identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `prospects: list[typing.Any] | None`
    :   Prospects

    `updated_at: str | None`
    :   Updated at

<a id="ProspectsSearchData"></a>

`ProspectsSearchData(**data: Any)`
:   Search result data for prospects entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: list[typing.Any] | None`
    :   Account

    `account_name: str | None`
    :   Account name

    `active_sequence_states: list[typing.Any] | None`
    :   Active sequence states

    `added_at: str | None`
    :   Added at

    `address_city: str | None`
    :   Address city

    `address_country: str | None`
    :   Address country

    `address_state: str | None`
    :   Address state

    `address_street: str | None`
    :   Address street

    `address_street2: str | None`
    :   Address street2

    `address_zip: str | None`
    :   Address zip

    `angel_list_url: str | None`
    :   Angel list url

    `assigned_teams: list[typing.Any] | None`
    :   Assigned teams

    `assigned_users: list[typing.Any] | None`
    :   Assigned users

    `available_at: str | None`
    :   Available at

    `batches: list[typing.Any] | None`
    :   Batches

    `call_opted_out: bool | None`
    :   Call opted out

    `calls: list[typing.Any] | None`
    :   Calls

    `calls_opt_status: str | None`
    :   Calls opt status

    `calls_opted_at: str | None`
    :   Calls opted at

    `campaign_name: str | None`
    :   Campaign name

    `click_count: int | None`
    :   Click count

    `company: str | None`
    :   Company

    `company_followers: int | None`
    :   Company followers

    `company_founded_at: str | None`
    :   Company founded at

    `company_industry: str | None`
    :   Company industry

    `company_linked_in: str | None`
    :   Company linked in

    `company_linked_in_employees: str | None`
    :   Company linked in employees

    `company_locality: str | None`
    :   Company locality

    `company_natural: str | None`
    :   Company natural

    `company_size: int | None`
    :   Company size

    `company_start_date: str | None`
    :   Company start date

    `company_type: str | None`
    :   Company type

    `contact_histogram: list[typing.Any] | None`
    :   Contact histogram

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `custom1: str | None`
    :   Custom field 1

    `custom10: str | None`
    :   Custom field 10

    `custom100: str | None`
    :   Custom field 100

    `custom101: str | None`
    :   Custom field 101

    `custom102: str | None`
    :   Custom field 102

    `custom103: str | None`
    :   Custom field 103

    `custom104: str | None`
    :   Custom field 104

    `custom105: str | None`
    :   Custom field 105

    `custom106: str | None`
    :   Custom field 106

    `custom107: str | None`
    :   Custom field 107

    `custom108: str | None`
    :   Custom field 108

    `custom109: str | None`
    :   Custom field 109

    `custom11: str | None`
    :   Custom field 11

    `custom110: str | None`
    :   Custom field 110

    `custom111: str | None`
    :   Custom field 111

    `custom112: str | None`
    :   Custom field 112

    `custom113: str | None`
    :   Custom field 113

    `custom114: str | None`
    :   Custom field 114

    `custom115: str | None`
    :   Custom field 115

    `custom116: str | None`
    :   Custom field 116

    `custom117: str | None`
    :   Custom field 117

    `custom118: str | None`
    :   Custom field 118

    `custom119: str | None`
    :   Custom field 119

    `custom12: str | None`
    :   Custom field 12

    `custom120: str | None`
    :   Custom field 120

    `custom121: str | None`
    :   Custom field 121

    `custom122: str | None`
    :   Custom field 122

    `custom123: str | None`
    :   Custom field 123

    `custom124: str | None`
    :   Custom field 124

    `custom125: str | None`
    :   Custom field 125

    `custom126: str | None`
    :   Custom field 126

    `custom127: str | None`
    :   Custom field 127

    `custom128: str | None`
    :   Custom field 128

    `custom129: str | None`
    :   Custom field 129

    `custom13: str | None`
    :   Custom field 13

    `custom130: str | None`
    :   Custom field 130

    `custom131: str | None`
    :   Custom field 131

    `custom132: str | None`
    :   Custom field 132

    `custom133: str | None`
    :   Custom field 133

    `custom134: str | None`
    :   Custom field 134

    `custom135: str | None`
    :   Custom field 135

    `custom136: str | None`
    :   Custom field 136

    `custom137: str | None`
    :   Custom field 137

    `custom138: str | None`
    :   Custom field 138

    `custom139: str | None`
    :   Custom field 139

    `custom14: str | None`
    :   Custom field 14

    `custom140: str | None`
    :   Custom field 140

    `custom141: str | None`
    :   Custom field 141

    `custom142: str | None`
    :   Custom field 142

    `custom143: str | None`
    :   Custom field 143

    `custom144: str | None`
    :   Custom field 144

    `custom145: str | None`
    :   Custom field 145

    `custom146: str | None`
    :   Custom field 146

    `custom147: str | None`
    :   Custom field 147

    `custom148: str | None`
    :   Custom field 148

    `custom149: str | None`
    :   Custom field 149

    `custom15: str | None`
    :   Custom field 15

    `custom150: str | None`
    :   Custom field 150

    `custom16: str | None`
    :   Custom field 16

    `custom17: str | None`
    :   Custom field 17

    `custom18: str | None`
    :   Custom field 18

    `custom19: str | None`
    :   Custom field 19

    `custom2: str | None`
    :   Custom field 2

    `custom20: str | None`
    :   Custom field 20

    `custom21: str | None`
    :   Custom field 21

    `custom22: str | None`
    :   Custom field 22

    `custom23: str | None`
    :   Custom field 23

    `custom24: str | None`
    :   Custom field 24

    `custom25: str | None`
    :   Custom field 25

    `custom26: str | None`
    :   Custom field 26

    `custom27: str | None`
    :   Custom field 27

    `custom28: str | None`
    :   Custom field 28

    `custom29: str | None`
    :   Custom field 29

    `custom3: str | None`
    :   Custom field 3

    `custom30: str | None`
    :   Custom field 30

    `custom31: str | None`
    :   Custom field 31

    `custom32: str | None`
    :   Custom field 32

    `custom33: str | None`
    :   Custom field 33

    `custom34: str | None`
    :   Custom field 34

    `custom35: str | None`
    :   Custom field 35

    `custom36: str | None`
    :   Custom field 36

    `custom37: str | None`
    :   Custom field 37

    `custom38: str | None`
    :   Custom field 38

    `custom39: str | None`
    :   Custom field 39

    `custom4: str | None`
    :   Custom field 4

    `custom40: str | None`
    :   Custom field 40

    `custom41: str | None`
    :   Custom field 41

    `custom42: str | None`
    :   Custom field 42

    `custom43: str | None`
    :   Custom field 43

    `custom44: str | None`
    :   Custom field 44

    `custom45: str | None`
    :   Custom field 45

    `custom46: str | None`
    :   Custom field 46

    `custom47: str | None`
    :   Custom field 47

    `custom48: str | None`
    :   Custom field 48

    `custom49: str | None`
    :   Custom field 49

    `custom5: str | None`
    :   Custom field 5

    `custom50: str | None`
    :   Custom field 50

    `custom51: str | None`
    :   Custom field 51

    `custom52: str | None`
    :   Custom field 52

    `custom53: str | None`
    :   Custom field 53

    `custom54: str | None`
    :   Custom field 54

    `custom55: str | None`
    :   Custom field 55

    `custom56: str | None`
    :   Custom field 56

    `custom57: str | None`
    :   Custom field 57

    `custom58: str | None`
    :   Custom field 58

    `custom59: str | None`
    :   Custom field 59

    `custom6: str | None`
    :   Custom field 6

    `custom60: str | None`
    :   Custom field 60

    `custom61: str | None`
    :   Custom field 61

    `custom62: str | None`
    :   Custom field 62

    `custom63: str | None`
    :   Custom field 63

    `custom64: str | None`
    :   Custom field 64

    `custom65: str | None`
    :   Custom field 65

    `custom66: str | None`
    :   Custom field 66

    `custom67: str | None`
    :   Custom field 67

    `custom68: str | None`
    :   Custom field 68

    `custom69: str | None`
    :   Custom field 69

    `custom7: str | None`
    :   Custom field 7

    `custom70: str | None`
    :   Custom field 70

    `custom71: str | None`
    :   Custom field 71

    `custom72: str | None`
    :   Custom field 72

    `custom73: str | None`
    :   Custom field 73

    `custom74: str | None`
    :   Custom field 74

    `custom75: str | None`
    :   Custom field 75

    `custom76: str | None`
    :   Custom field 76

    `custom77: str | None`
    :   Custom field 77

    `custom78: str | None`
    :   Custom field 78

    `custom79: str | None`
    :   Custom field 79

    `custom8: str | None`
    :   Custom field 8

    `custom80: str | None`
    :   Custom field 80

    `custom81: str | None`
    :   Custom field 81

    `custom82: str | None`
    :   Custom field 82

    `custom83: str | None`
    :   Custom field 83

    `custom84: str | None`
    :   Custom field 84

    `custom85: str | None`
    :   Custom field 85

    `custom86: str | None`
    :   Custom field 86

    `custom87: str | None`
    :   Custom field 87

    `custom88: str | None`
    :   Custom field 88

    `custom89: str | None`
    :   Custom field 89

    `custom9: str | None`
    :   Custom field 9

    `custom90: str | None`
    :   Custom field 90

    `custom91: str | None`
    :   Custom field 91

    `custom92: str | None`
    :   Custom field 92

    `custom93: str | None`
    :   Custom field 93

    `custom94: str | None`
    :   Custom field 94

    `custom95: str | None`
    :   Custom field 95

    `custom96: str | None`
    :   Custom field 96

    `custom97: str | None`
    :   Custom field 97

    `custom98: str | None`
    :   Custom field 98

    `custom99: str | None`
    :   Custom field 99

    `date_of_birth: str | None`
    :   Date of birth

    `default_plugin_mapping: list[typing.Any] | None`
    :   Default plugin mapping

    `degree: str | None`
    :   Degree

    `email_addresses: list[typing.Any] | None`
    :   Email addresses

    `email_contacts: list[typing.Any] | None`
    :   Email contacts

    `email_opted_out: bool | None`
    :   Email opted out

    `emails: list[typing.Any] | None`
    :   Emails

    `emails_opt_status: str | None`
    :   Emails opt status

    `emails_opted_at: str | None`
    :   Emails opted at

    `engaged_at: str | None`
    :   Engaged at

    `engaged_score: float | None`
    :   Engaged score

    `event_name: str | None`
    :   Event name

    `external_id: str | None`
    :   External id

    `external_owner: str | None`
    :   External owner

    `external_source: str | None`
    :   External source

    `facebook_url: str | None`
    :   Facebook url

    `favorites: list[typing.Any] | None`
    :   Favorites

    `first_name: str | None`
    :   First name

    `gender: str | None`
    :   Gender

    `github_url: str | None`
    :   Github url

    `github_username: str | None`
    :   Github username

    `google_plus_url: str | None`
    :   Google plus url

    `graduation_date: str | None`
    :   Graduation date

    `home_phones: list[typing.Any] | None`
    :   Home phones

    `id: int | None`
    :   Unique prospect identifier

    `job_start_date: str | None`
    :   Job start date

    `last_name: str | None`
    :   Last name

    `linked_in_connections: int | None`
    :   Linked in connections

    `linked_in_id: str | None`
    :   Linked in id

    `linked_in_slug: str | None`
    :   Linked in slug

    `linked_in_url: str | None`
    :   Linked in url

    `mailings: list[typing.Any] | None`
    :   Mailings

    `middle_name: str | None`
    :   Middle name

    `mobile_phones: list[typing.Any] | None`
    :   Mobile phones

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `nickname: str | None`
    :   Nickname

    `occupation: str | None`
    :   Occupation

    `open_count: int | None`
    :   Open count

    `opportunities: list[typing.Any] | None`
    :   Opportunities

    `opportunity_prospect_roles: list[typing.Any] | None`
    :   Opportunity prospect roles

    `opted_out: bool | None`
    :   Opted out

    `opted_out_at: str | None`
    :   Opted out at

    `other_phones: list[typing.Any] | None`
    :   Other phones

    `owner: list[typing.Any] | None`
    :   Owner

    `persona: list[typing.Any] | None`
    :   Persona

    `persona_name: str | None`
    :   Persona name

    `personal_note1: str | None`
    :   Personal note1

    `personal_note2: str | None`
    :   Personal note2

    `phone_numbers: list[typing.Any] | None`
    :   Phone numbers

    `preferred_contact: str | None`
    :   Preferred contact

    `quora_url: str | None`
    :   Quora url

    `region: str | None`
    :   Region

    `reply_count: int | None`
    :   Reply count

    `school: str | None`
    :   School

    `score: float | None`
    :   Score

    `sequence_states: list[typing.Any] | None`
    :   Sequence states

    `sharing_team_id: str | None`
    :   Sharing team id

    `sms_opt_status: str | None`
    :   Sms opt status

    `sms_opted_at: str | None`
    :   Sms opted at

    `sms_opted_out: bool | None`
    :   Sms opted out

    `source: str | None`
    :   Source

    `specialties: str | None`
    :   Specialties

    `stack_overflow_id: str | None`
    :   Stack overflow id

    `stack_overflow_url: str | None`
    :   Stack overflow url

    `stage: list[typing.Any] | None`
    :   Stage

    `stage_name: str | None`
    :   Stage name

    `tags: list[typing.Any] | None`
    :   Tags

    `tasks: list[typing.Any] | None`
    :   Tasks

    `time_zone: str | None`
    :   Time zone

    `time_zone_iana: str | None`
    :   Time zone iana

    `time_zone_inferred: str | None`
    :   Time zone inferred

    `title: str | None`
    :   Title

    `touched_at: str | None`
    :   Touched at

    `trashed_at: str | None`
    :   Trashed at

    `trashed_by_account: list[typing.Any] | None`
    :   Trashed by account

    `twitter_url: str | None`
    :   Twitter url

    `twitter_username: str | None`
    :   Twitter username

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

    `updater_id: int | None`
    :   Updater id

    `updater_type: str | None`
    :   Updater type

    `voip_phones: list[typing.Any] | None`
    :   Voip phones

    `website_url1: str | None`
    :   Website url1

    `website_url2: str | None`
    :   Website url2

    `website_url3: str | None`
    :   Website url3

    `work_phones: list[typing.Any] | None`
    :   Work phones

<a id="SequenceStatesSearchData"></a>

`SequenceStatesSearchData(**data: Any)`
:   Search result data for sequence_states entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: list[typing.Any] | None`
    :   Account

    `active_at: str | None`
    :   Active at

    `active_step_mailings: list[typing.Any] | None`
    :   Active step mailings

    `active_step_tasks: list[typing.Any] | None`
    :   Active step tasks

    `bounce_count: int | None`
    :   Bounce count

    `call_completed_at: str | None`
    :   Call completed at

    `calls: list[typing.Any] | None`
    :   Calls

    `click_count: int | None`
    :   Click count

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `deliver_count: int | None`
    :   Deliver count

    `error_reason: str | None`
    :   Error reason

    `failure_count: int | None`
    :   Failure count

    `id: int | None`
    :   Unique sequence state identifier

    `mailbox: list[typing.Any] | None`
    :   Mailbox

    `mailings: list[typing.Any] | None`
    :   Mailings

    `model_config`
    :   The type of the None singleton.

    `negative_reply_count: int | None`
    :   Negative reply count

    `neutral_reply_count: int | None`
    :   Neutral reply count

    `open_count: int | None`
    :   Open count

    `opportunity: list[typing.Any] | None`
    :   Opportunity

    `opt_out_count: int | None`
    :   Opt out count

    `pause_reason: str | None`
    :   Pause reason

    `positive_reply_count: int | None`
    :   Positive reply count

    `prospect: list[typing.Any] | None`
    :   Prospect

    `replied_at: str | None`
    :   Replied at

    `reply_count: int | None`
    :   Reply count

    `schedule_count: int | None`
    :   Schedule count

    `sequence: list[typing.Any] | None`
    :   Sequence

    `sequence_step: list[typing.Any] | None`
    :   Sequence step

    `state: str | None`
    :   State

    `state_changed_at: str | None`
    :   State changed at

    `tasks: list[typing.Any] | None`
    :   Tasks

    `updated_at: str | None`
    :   Updated at

<a id="SequenceStepsSearchData"></a>

`SequenceStepsSearchData(**data: Any)`
:   Search result data for sequence_steps entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bounce_count: int | None`
    :   Bounce count

    `call_purpose: list[typing.Any] | None`
    :   Call purpose

    `calls: list[typing.Any] | None`
    :   Calls

    `click_count: int | None`
    :   Click count

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `date: str | None`
    :   Date

    `deliver_count: int | None`
    :   Deliver count

    `display_name: str | None`
    :   Display name

    `failure_count: int | None`
    :   Failure count

    `id: int | None`
    :   Unique sequence step identifier

    `interval: int | None`
    :   Interval

    `mailings: list[typing.Any] | None`
    :   Mailings

    `model_config`
    :   The type of the None singleton.

    `negative_reply_count: int | None`
    :   Negative reply count

    `neutral_reply_count: int | None`
    :   Neutral reply count

    `open_count: int | None`
    :   Open count

    `opt_out_count: int | None`
    :   Opt out count

    `order: int | None`
    :   Order

    `positive_reply_count: int | None`
    :   Positive reply count

    `reply_count: int | None`
    :   Reply count

    `schedule_count: int | None`
    :   Schedule count

    `sequence: list[typing.Any] | None`
    :   Sequence

    `sequence_templates: list[typing.Any] | None`
    :   Sequence templates

    `step_type: str | None`
    :   Step type

    `task_auto_display: str | None`
    :   Task auto display

    `task_priority: list[typing.Any] | None`
    :   Task priority

    `tasks: list[typing.Any] | None`
    :   Tasks

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

<a id="SequencesSearchData"></a>

`SequencesSearchData(**data: Any)`
:   Search result data for sequences entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `automation_percentage: float | None`
    :   Automation percentage

    `bounce_count: int | None`
    :   Bounce count

    `calls: list[typing.Any] | None`
    :   Calls

    `click_count: int | None`
    :   Click count

    `content_category_memberships: list[typing.Any] | None`
    :   Content category memberships

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `deliver_count: int | None`
    :   Deliver count

    `description: str | None`
    :   Description

    `duration_in_days: int | None`
    :   Duration in days

    `enabled: bool | None`
    :   Enabled

    `enabled_at: str | None`
    :   Enabled at

    `failure_count: int | None`
    :   Failure count

    `finish_on_reply: bool | None`
    :   Finish on reply

    `id: int | None`
    :   Unique sequence identifier

    `last_used_at: str | None`
    :   Last used at

    `locked: bool | None`
    :   Locked

    `locked_at: str | None`
    :   Locked at

    `mailings: list[typing.Any] | None`
    :   Mailings

    `max_activations: int | None`
    :   Max activations

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `negative_reply_count: int | None`
    :   Negative reply count

    `neutral_reply_count: int | None`
    :   Neutral reply count

    `num_contacted_prospects: int | None`
    :   Num contacted prospects

    `num_replied_prospects: int | None`
    :   Num replied prospects

    `open_count: int | None`
    :   Open count

    `opt_out_count: int | None`
    :   Opt out count

    `owner: list[typing.Any] | None`
    :   Owner

    `positive_reply_count: int | None`
    :   Positive reply count

    `primary_reply_action: str | None`
    :   Primary reply action

    `primary_reply_pause_duration: int | None`
    :   Primary reply pause duration

    `reply_count: int | None`
    :   Reply count

    `ruleset: list[typing.Any] | None`
    :   Ruleset

    `schedule: list[typing.Any] | None`
    :   Schedule

    `schedule_count: int | None`
    :   Schedule count

    `schedule_interval_type: str | None`
    :   Schedule interval type

    `secondary_reply_action: str | None`
    :   Secondary reply action

    `secondary_reply_pause_duration: int | None`
    :   Secondary reply pause duration

    `sequence_states: list[typing.Any] | None`
    :   Sequence states

    `sequence_step_count: int | None`
    :   Sequence step count

    `sequence_steps: list[typing.Any] | None`
    :   Sequence steps

    `sequence_type: str | None`
    :   Sequence type

    `share_type: str | None`
    :   Share type

    `tags: list[typing.Any] | None`
    :   Tags

    `tasks: list[typing.Any] | None`
    :   Tasks

    `throttle_capacity: int | None`
    :   Throttle capacity

    `throttle_max_adds_per_day: int | None`
    :   Throttle max adds per day

    `throttle_paused: bool | None`
    :   Throttle paused

    `throttle_paused_at: str | None`
    :   Throttle paused at

    `transactional: bool | None`
    :   Transactional

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

<a id="SnippetsSearchData"></a>

`SnippetsSearchData(**data: Any)`
:   Search result data for snippets entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body_html: str | None`
    :   Body html

    `body_text: str | None`
    :   Body text

    `content_category_memberships: list[typing.Any] | None`
    :   Content category memberships

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `id: int | None`
    :   Unique snippet identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `owner: list[typing.Any] | None`
    :   Owner

    `share_type: str | None`
    :   Share type

    `tags: str | None`
    :   Tags

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

<a id="StagesSearchData"></a>

`StagesSearchData(**data: Any)`
:   Search result data for stages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Color

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `id: int | None`
    :   Unique stage identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `order: int | None`
    :   Order

    `prospects: list[typing.Any] | None`
    :   Prospects

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

<a id="TasksSearchData"></a>

`TasksSearchData(**data: Any)`
:   Search result data for tasks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: list[typing.Any] | None`
    :   Account

    `action: str | None`
    :   Action

    `autoskip_at: str | None`
    :   Autoskip at

    `call: list[typing.Any] | None`
    :   Call

    `calls: list[typing.Any] | None`
    :   Calls

    `compiled_sequence_template_html: str | None`
    :   Compiled sequence template html

    `completed: bool | None`
    :   Completed

    `completed_at: str | None`
    :   Completed at

    `completer: list[typing.Any] | None`
    :   Completer

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `default_plugin_mapping: list[typing.Any] | None`
    :   Default plugin mapping

    `due_at: str | None`
    :   Due at

    `id: int | None`
    :   Unique task identifier

    `mailing: list[typing.Any] | None`
    :   Mailing

    `mailings: list[typing.Any] | None`
    :   Mailings

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Note

    `opportunity: list[typing.Any] | None`
    :   Opportunity

    `opportunity_association: str | None`
    :   Opportunity association

    `owner: list[typing.Any] | None`
    :   Owner

    `prospect: list[typing.Any] | None`
    :   Prospect

    `prospect_account: list[typing.Any] | None`
    :   Prospect account

    `prospect_contacts: list[typing.Any] | None`
    :   Prospect contacts

    `prospect_owner: list[typing.Any] | None`
    :   Prospect owner

    `prospect_phone_numbers: list[typing.Any] | None`
    :   Prospect phone numbers

    `prospect_stage: list[typing.Any] | None`
    :   Prospect stage

    `scheduled_at: str | None`
    :   Scheduled at

    `sequence: list[typing.Any] | None`
    :   Sequence

    `sequence_sequence_steps: list[typing.Any] | None`
    :   Sequence sequence steps

    `sequence_state: list[typing.Any] | None`
    :   Sequence state

    `sequence_state_sequence_step: list[typing.Any] | None`
    :   Sequence state sequence step

    `sequence_state_sequence_step_overrides: list[typing.Any] | None`
    :   Sequence state sequence step overrides

    `sequence_state_starting_template: list[typing.Any] | None`
    :   Sequence state starting template

    `sequence_step: list[typing.Any] | None`
    :   Sequence step

    `sequence_step_override_templates: list[typing.Any] | None`
    :   Sequence step override templates

    `sequence_template: list[typing.Any] | None`
    :   Sequence template

    `sequence_template_template: list[typing.Any] | None`
    :   Sequence template template

    `state: str | None`
    :   State

    `state_changed_at: str | None`
    :   State changed at

    `subject: list[typing.Any] | None`
    :   Subject

    `task_priority: list[typing.Any] | None`
    :   Task priority

    `task_theme: list[typing.Any] | None`
    :   Task theme

    `task_type: str | None`
    :   Task type

    `template: list[typing.Any] | None`
    :   Template

    `updated_at: str | None`
    :   Updated at

<a id="TemplatesSearchData"></a>

`TemplatesSearchData(**data: Any)`
:   Search result data for templates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Archived

    `archived_at: str | None`
    :   Archived at

    `bcc_recipients: str | None`
    :   Bcc recipients

    `body_html: str | None`
    :   Body html

    `body_text: str | None`
    :   Body text

    `bounce_count: int | None`
    :   Bounce count

    `cc_recipients: str | None`
    :   Cc recipients

    `click_count: int | None`
    :   Click count

    `content_category_memberships: list[typing.Any] | None`
    :   Content category memberships

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `deliver_count: int | None`
    :   Deliver count

    `failure_count: int | None`
    :   Failure count

    `id: int | None`
    :   Unique template identifier

    `last_used_at: str | None`
    :   Last used at

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `negative_reply_count: int | None`
    :   Negative reply count

    `neutral_reply_count: int | None`
    :   Neutral reply count

    `open_count: int | None`
    :   Open count

    `opt_out_count: int | None`
    :   Opt out count

    `owner: list[typing.Any] | None`
    :   Owner

    `positive_reply_count: int | None`
    :   Positive reply count

    `recipients: list[typing.Any] | None`
    :   Recipients

    `reply_count: int | None`
    :   Reply count

    `schedule_count: int | None`
    :   Schedule count

    `sequence_templates: list[typing.Any] | None`
    :   Sequence templates

    `share_type: str | None`
    :   Share type

    `subject: str | None`
    :   Subject

    `tags: str | None`
    :   Tags

    `to_recipients: str | None`
    :   To recipients

    `track_links: bool | None`
    :   Track links

    `track_opens: bool | None`
    :   Track opens

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

<a id="UsersSearchData"></a>

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accounts_view_id: int | None`
    :   Accounts view id

    `active_prospects_count: int | None`
    :   Active prospects count

    `activity_notifications_disabled: bool | None`
    :   Activity notifications disabled

    `batches: list[typing.Any] | None`
    :   Batches

    `batches_view_id: int | None`
    :   Batches view id

    `bounce_warning_email_enabled: bool | None`
    :   Bounce warning email enabled

    `bridge_phone: str | None`
    :   Bridge phone

    `bridge_phone_extension: str | None`
    :   Bridge phone extension

    `buyer_language_preference: str | None`
    :   Buyer language preference

    `calendar: list[typing.Any] | None`
    :   Calendar

    `calendar_events_view_id: int | None`
    :   Calendar events view id

    `calls_view_id: int | None`
    :   Calls view id

    `content_categories: list[typing.Any] | None`
    :   Content categories

    `content_category_ownerships: list[typing.Any] | None`
    :   Content category ownerships

    `controlled_tab_default: str | None`
    :   Controlled tab default

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `current_sign_in_at: str | None`
    :   Current sign in at

    `custom1: str | None`
    :   Custom field 1

    `custom2: str | None`
    :   Custom field 2

    `custom3: str | None`
    :   Custom field 3

    `custom4: str | None`
    :   Custom field 4

    `custom5: str | None`
    :   Custom field 5

    `daily_digest_email_enabled: bool | None`
    :   Daily digest email enabled

    `default_ruleset_id: int | None`
    :   Default ruleset id

    `default_schedule_id: int | None`
    :   Default schedule id

    `duties: list[typing.Any] | None`
    :   Duties

    `duties_set_at: str | None`
    :   Duties set at

    `email: str | None`
    :   Email

    `enable_voice_recordings: bool | None`
    :   Enable voice recordings

    `engagement_emails_enabled: bool | None`
    :   Engagement emails enabled

    `favorites: list[typing.Any] | None`
    :   Favorites

    `first_name: str | None`
    :   First name

    `global_id: str | None`
    :   Global id

    `id: int | None`
    :   Unique user identifier

    `imports_view_id: int | None`
    :   Imports view id

    `inbound_bridge_phone: str | None`
    :   Inbound bridge phone

    `inbound_bridge_phone_extension: str | None`
    :   Inbound bridge phone extension

    `inbound_call_behavior: str | None`
    :   Inbound call behavior

    `inbound_phone_type: str | None`
    :   Inbound phone type

    `inbound_voicemail_custom_message_text: str | None`
    :   Inbound voicemail custom message text

    `inbound_voicemail_message_text_voice: str | None`
    :   Inbound voicemail message text voice

    `inbound_voicemail_prompt_type: str | None`
    :   Inbound voicemail prompt type

    `job_role: list[typing.Any] | None`
    :   Job role

    `kaia_recordings_view_id: int | None`
    :   Kaia recordings view id

    `keep_bridge_phone_connected: bool | None`
    :   Keep bridge phone connected

    `language_preference: str | None`
    :   Language preference

    `last_name: str | None`
    :   Last name

    `last_sign_in_at: str | None`
    :   Last sign in at

    `link_to_sequence_state_in_task_flow: bool | None`
    :   Link to sequence state in task flow

    `live_listen_view_id: int | None`
    :   Live listen view id

    `locked: bool | None`
    :   Locked

    `mailbox: list[typing.Any] | None`
    :   Mailbox

    `mailbox_error_email_enabled: bool | None`
    :   Mailbox error email enabled

    `mailboxes: list[typing.Any] | None`
    :   Mailboxes

    `mailings_delivered_count: int | None`
    :   Mailings delivered count

    `mailings_replied_count: int | None`
    :   Mailings replied count

    `mailings_view_id: int | None`
    :   Mailings view id

    `meeting_engagement_notification_enabled: bool | None`
    :   Meeting engagement notification enabled

    `meeting_types_view_id: int | None`
    :   Meeting types view id

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name

    `notifications_enabled: bool | None`
    :   Notifications enabled

    `oce_click_to_dial_everywhere: bool | None`
    :   Oce click to dial everywhere

    `oce_gmail_toolbar: bool | None`
    :   Oce gmail toolbar

    `oce_gmail_tracking_state: str | None`
    :   Oce gmail tracking state

    `oce_salesforce_email_decorating: bool | None`
    :   Oce salesforce email decorating

    `oce_salesforce_phone_decorating: bool | None`
    :   Oce salesforce phone decorating

    `oce_universal_task_flow: bool | None`
    :   Oce universal task flow

    `oce_window_mode: bool | None`
    :   Oce window mode

    `onboarded_at: str | None`
    :   Onboarded at

    `opportunities_view_id: int | None`
    :   Opportunities view id

    `orca_standalone_enabled: bool | None`
    :   Orca standalone enabled

    `outbound_voicemails: list[typing.Any] | None`
    :   Outbound voicemails

    `password_expires_at: str | None`
    :   Password expires at

    `phone: list[typing.Any] | None`
    :   Phone

    `phone_country_code: str | None`
    :   Phone country code

    `phone_number: str | None`
    :   Phone number

    `phone_type: str | None`
    :   Phone type

    `phones: list[typing.Any] | None`
    :   Phones

    `phones_view_id: int | None`
    :   Phones view id

    `plugin_alert_notification_enabled: bool | None`
    :   Plugin alert notification enabled

    `preferred_voice_region: str | None`
    :   Preferred voice region

    `prefers_local_presence: bool | None`
    :   Prefers local presence

    `primary_timezone: str | None`
    :   Primary timezone

    `profile: list[typing.Any] | None`
    :   Profile

    `prospect_detail_default: str | None`
    :   Prospect detail default

    `prospects_view_id: int | None`
    :   Prospects view id

    `recipients: list[typing.Any] | None`
    :   Recipients

    `reports_sequence_performance_view_id: int | None`
    :   Reports sequence performance view id

    `reports_team_perf_view_id: int | None`
    :   Reports team perf view id

    `reports_team_performance_intraday_view_id: int | None`
    :   Reports team performance intraday view id

    `reports_team_performance_view_id: int | None`
    :   Reports team performance view id

    `reports_view_id: int | None`
    :   Reports view id

    `role: list[typing.Any] | None`
    :   Role

    `scim_external_id: str | None`
    :   Scim external id

    `scim_source: str | None`
    :   Scim source

    `secondary_timezone: str | None`
    :   Secondary timezone

    `send_invite_fallback: bool | None`
    :   Send invite fallback

    `sender_notifications_excluded: bool | None`
    :   Sender notifications excluded

    `sequence_states_view_id: int | None`
    :   Sequence states view id

    `sequences_view_id: int | None`
    :   Sequences view id

    `sms_phone: list[typing.Any] | None`
    :   Sms phone

    `snippets_view_id: int | None`
    :   Snippets view id

    `tasks_due_count: int | None`
    :   Tasks due count

    `tasks_view_id: int | None`
    :   Tasks view id

    `teams: list[typing.Any] | None`
    :   Teams

    `teams_view_id: int | None`
    :   Teams view id

    `templates_view_id: int | None`
    :   Templates view id

    `tertiary_timezone: str | None`
    :   Tertiary timezone

    `texting_email_notifications: bool | None`
    :   Texting email notifications

    `title: str | None`
    :   Title

    `unknown_reply_email_enabled: bool | None`
    :   Unknown reply email enabled

    `updated_at: str | None`
    :   Updated at

    `updater: list[typing.Any] | None`
    :   Updater

    `use_sales_navigator_for_linked_in_tasks: bool | None`
    :   Use sales navigator for linked in tasks

    `user_guid: str | None`
    :   User guid

    `username: str | None`
    :   Username

    `users_view_id: int | None`
    :   Users view id

    `voicemail_notification_enabled: bool | None`
    :   Voicemail notification enabled

    `voicemail_prompts: list[typing.Any] | None`
    :   Voicemail prompts

    `weekly_digest_email_enabled: bool | None`
    :   Weekly digest email enabled