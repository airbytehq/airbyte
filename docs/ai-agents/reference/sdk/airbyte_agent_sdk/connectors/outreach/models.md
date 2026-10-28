---
id: airbyte_agent_sdk-connectors-outreach-models
title: airbyte_agent_sdk.connectors.outreach.models
---

Module airbyte_agent_sdk.connectors.outreach.models
===================================================
Pydantic models for outreach connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Account"></a>

`Account(**data: Any)`
:   Outreach account object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.AccountAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.AccountLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="AccountAttributes"></a>

`AccountAttributes(**data: Any)`
:   Nested schema for Account.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annual_revenue_range: str | None`
    :   Define the annual revenue range

    `buyer_intent_score: float | None`
    :   A custom score given to measure the quality of the account.

    `company_type: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom1: str | None`
    :   The value of the account’s first custom field.

    `custom10: str | None`
    :   The value of the account’s 10th custom field.

    `custom100: str | None`
    :   The value of the account’s 100th custom field.

    `custom101: str | None`
    :   The value of the account’s 101st custom field.

    `custom102: str | None`
    :   The value of the account’s 102nd custom field.

    `custom103: str | None`
    :   The value of the account’s 103rd custom field.

    `custom104: str | None`
    :   The value of the account’s 104th custom field.

    `custom105: str | None`
    :   The value of the account’s 105th custom field.

    `custom106: str | None`
    :   The value of the account’s 106th custom field.

    `custom107: str | None`
    :   The value of the account’s 107th custom field.

    `custom108: str | None`
    :   The value of the account’s 108th custom field.

    `custom109: str | None`
    :   The value of the account’s 109th custom field.

    `custom11: str | None`
    :   The value of the account’s 11th custom field.

    `custom110: str | None`
    :   The value of the account’s 110th custom field.

    `custom111: str | None`
    :   The value of the account’s 111th custom field.

    `custom112: str | None`
    :   The value of the account’s 112th custom field.

    `custom113: str | None`
    :   The value of the account’s 113th custom field.

    `custom114: str | None`
    :   The value of the account’s 114th custom field.

    `custom115: str | None`
    :   The value of the account’s 115th custom field.

    `custom116: str | None`
    :   The value of the account’s 116th custom field.

    `custom117: str | None`
    :   The value of the account’s 117th custom field.

    `custom118: str | None`
    :   The value of the account’s 118th custom field.

    `custom119: str | None`
    :   The value of the account’s 119th custom field.

    `custom12: str | None`
    :   The value of the account’s 12th custom field.

    `custom120: str | None`
    :   The value of the account’s 120th custom field.

    `custom121: str | None`
    :   The value of the account’s 121st custom field.

    `custom122: str | None`
    :   The value of the account’s 122nd custom field.

    `custom123: str | None`
    :   The value of the account’s 123rd custom field.

    `custom124: str | None`
    :   The value of the account’s 124th custom field.

    `custom125: str | None`
    :   The value of the account’s 125th custom field.

    `custom126: str | None`
    :   The value of the account’s 126th custom field.

    `custom127: str | None`
    :   The value of the account’s 127th custom field.

    `custom128: str | None`
    :   The value of the account’s 128th custom field.

    `custom129: str | None`
    :   The value of the account’s 129th custom field.

    `custom13: str | None`
    :   The value of the account’s 13th custom field.

    `custom130: str | None`
    :   The value of the account’s 130th custom field.

    `custom131: str | None`
    :   The value of the account’s 131st custom field.

    `custom132: str | None`
    :   The value of the account’s 132nd custom field.

    `custom133: str | None`
    :   The value of the account’s 133rd custom field.

    `custom134: str | None`
    :   The value of the account’s 134th custom field.

    `custom135: str | None`
    :   The value of the account’s 135th custom field.

    `custom136: str | None`
    :   The value of the account’s 136th custom field.

    `custom137: str | None`
    :   The value of the account’s 137th custom field.

    `custom138: str | None`
    :   The value of the account’s 138th custom field.

    `custom139: str | None`
    :   The value of the account’s 139th custom field.

    `custom14: str | None`
    :   The value of the account’s 14th custom field.

    `custom140: str | None`
    :   The value of the account’s 140th custom field.

    `custom141: str | None`
    :   The value of the account’s 141st custom field.

    `custom142: str | None`
    :   The value of the account’s 142nd custom field.

    `custom143: str | None`
    :   The value of the account’s 143rd custom field.

    `custom144: str | None`
    :   The value of the account’s 144th custom field.

    `custom145: str | None`
    :   The value of the account’s 145th custom field.

    `custom146: str | None`
    :   The value of the account’s 146th custom field.

    `custom147: str | None`
    :   The value of the account’s 147th custom field.

    `custom148: str | None`
    :   The value of the account’s 148th custom field.

    `custom149: str | None`
    :   The value of the account’s 149th custom field.

    `custom15: str | None`
    :   The value of the account’s 15th custom field.

    `custom150: str | None`
    :   The value of the account’s 150th custom field.

    `custom16: str | None`
    :   The value of the account’s 16th custom field.

    `custom17: str | None`
    :   The value of the account’s 17th custom field.

    `custom18: str | None`
    :   The value of the account’s 18th custom field.

    `custom19: str | None`
    :   The value of the account’s 19th custom field.

    `custom2: str | None`
    :   The value of the account’s second custom field.

    `custom20: str | None`
    :   The value of the account’s 20th custom field.

    `custom21: str | None`
    :   The value of the account’s 21st custom field.

    `custom22: str | None`
    :   The value of the account’s 22nd custom field.

    `custom23: str | None`
    :   The value of the account’s 23rd custom field.

    `custom24: str | None`
    :   The value of the account’s 24th custom field.

    `custom25: str | None`
    :   The value of the account’s 25th custom field.

    `custom26: str | None`
    :   The value of the account’s 26th custom field.

    `custom27: str | None`
    :   The value of the account’s 27th custom field.

    `custom28: str | None`
    :   The value of the account’s 28th custom field.

    `custom29: str | None`
    :   The value of the account’s 29th custom field.

    `custom3: str | None`
    :   The value of the account’s third custom field.

    `custom30: str | None`
    :   The value of the account’s 30th custom field.

    `custom31: str | None`
    :   The value of the account’s 31st custom field.

    `custom32: str | None`
    :   The value of the account’s 32nd custom field.

    `custom33: str | None`
    :   The value of the account’s 33rd custom field.

    `custom34: str | None`
    :   The value of the account’s 34th custom field.

    `custom35: str | None`
    :   The value of the account’s 35th custom field.

    `custom36: str | None`
    :   The value of the account's 36th custom field.

    `custom37: str | None`
    :   The value of the account's 37th custom field.

    `custom38: str | None`
    :   The value of the account's 38th custom field.

    `custom39: str | None`
    :   The value of the account's 39th custom field.

    `custom4: str | None`
    :   The value of the account’s fourth custom field.

    `custom40: str | None`
    :   The value of the account's 40th custom field.

    `custom41: str | None`
    :   The value of the account's 41st custom field.

    `custom42: str | None`
    :   The value of the account's 42nd custom field.

    `custom43: str | None`
    :   The value of the account's 43rd custom field.

    `custom44: str | None`
    :   The value of the account's 44th custom field.

    `custom45: str | None`
    :   The value of the account's 45th custom field.

    `custom46: str | None`
    :   The value of the account's 46th custom field.

    `custom47: str | None`
    :   The value of the account's 47th custom field.

    `custom48: str | None`
    :   The value of the account's 48th custom field.

    `custom49: str | None`
    :   The value of the account's 49th custom field.

    `custom5: str | None`
    :   The value of the account’s fifth custom field.

    `custom50: str | None`
    :   The value of the account's 50th custom field.

    `custom51: str | None`
    :   The value of the account's 51st custom field.

    `custom52: str | None`
    :   The value of the account's 52nd custom field.

    `custom53: str | None`
    :   The value of the account's 53rd custom field.

    `custom54: str | None`
    :   The value of the account's 54th custom field.

    `custom55: str | None`
    :   The value of the account's 55th custom field.

    `custom56: str | None`
    :   The value of the account's 56th custom field.

    `custom57: str | None`
    :   The value of the account's 57th custom field.

    `custom58: str | None`
    :   The value of the account's 58th custom field.

    `custom59: str | None`
    :   The value of the account's 59th custom field.

    `custom6: str | None`
    :   The value of the account’s sixth custom field.

    `custom60: str | None`
    :   The value of the account's 60th custom field.

    `custom61: str | None`
    :   The value of the account's 61st custom field.

    `custom62: str | None`
    :   The value of the account's 62nd custom field.

    `custom63: str | None`
    :   The value of the account's 63rd custom field.

    `custom64: str | None`
    :   The value of the account's 64th custom field.

    `custom65: str | None`
    :   The value of the account's 65th custom field.

    `custom66: str | None`
    :   The value of the account's 66th custom field.

    `custom67: str | None`
    :   The value of the account's 67th custom field.

    `custom68: str | None`
    :   The value of the account's 68th custom field.

    `custom69: str | None`
    :   The value of the account's 69th custom field.

    `custom7: str | None`
    :   The value of the account’s seventh custom field.

    `custom70: str | None`
    :   The value of the account's 70th custom field.

    `custom71: str | None`
    :   The value of the account's 71st custom field.

    `custom72: str | None`
    :   The value of the account's 72nd custom field.

    `custom73: str | None`
    :   The value of the account's 73rd custom field.

    `custom74: str | None`
    :   The value of the account's 74th custom field.

    `custom75: str | None`
    :   The value of the account's 75th custom field.

    `custom76: str | None`
    :   The value of the account's 76th custom field.

    `custom77: str | None`
    :   The value of the account's 77th custom field.

    `custom78: str | None`
    :   The value of the account's 78th custom field.

    `custom79: str | None`
    :   The value of the account's 79th custom field.

    `custom8: str | None`
    :   The value of the account’s eight custom field.

    `custom80: str | None`
    :   The value of the account's 80th custom field.

    `custom81: str | None`
    :   The value of the account's 81st custom field.

    `custom82: str | None`
    :   The value of the account's 82nd custom field.

    `custom83: str | None`
    :   The value of the account's 83rd custom field.

    `custom84: str | None`
    :   The value of the account's 84th custom field.

    `custom85: str | None`
    :   The value of the account's 85th custom field.

    `custom86: str | None`
    :   The value of the account's 86th custom field.

    `custom87: str | None`
    :   The value of the account's 87th custom field.

    `custom88: str | None`
    :   The value of the account's 88th custom field.

    `custom89: str | None`
    :   The value of the account's 89th custom field.

    `custom9: str | None`
    :   The value of the account’s ninth custom field.

    `custom90: str | None`
    :   The value of the account's 90th custom field.

    `custom91: str | None`
    :   The value of the account's 91st custom field.

    `custom92: str | None`
    :   The value of the account's 92nd custom field.

    `custom93: str | None`
    :   The value of the account's 93rd custom field.

    `custom94: str | None`
    :   The value of the account's 94th custom field.

    `custom95: str | None`
    :   The value of the account's 95th custom field.

    `custom96: str | None`
    :   The value of the account's 96th custom field.

    `custom97: str | None`
    :   The value of the account's 97th custom field.

    `custom98: str | None`
    :   The value of the account's 98th custom field.

    `custom99: str | None`
    :   The value of the account's 99th custom field.

    `custom_id: str | None`
    :   A custom ID for the account, often referencing an ID in an external system.

    `description: str | None`
    :   A custom description of the account.

    `domain: str | None`
    :   The type of the None singleton.

    `enrichable: bool | None`
    :   Enrichable

    `external_source: str | None`
    :   The source of the resource’s creation (e.g. 'outreach-api').

    `followers: int | None`
    :   The number of followers the company has listed on social media.

    `founded_at: str | None`
    :   The founding date of the company.

    `industry: str | None`
    :   The type of the None singleton.

    `linked_in_employees: int | None`
    :   The number of employees listed on the company’s LinkedIn URL.

    `linked_in_url: str | None`
    :   The company’s LinkedIn URL.

    `locality: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `naics_codes: list[str] | None`
    :   Define codes used to classify businesses by industry

    `name: str | None`
    :   The type of the None singleton.

    `named: bool | None`
    :   A boolean value determining whether this is a 'named' account or not. Only named accounts will show up on the collection index.

    `natural_name: str | None`
    :   The natural name of the company (e.g. 'Acme').

    `number_of_employees: int | None`
    :   The type of the None singleton.

    `sharing_team_id: str | None`
    :   The ID of the sharing team associated with this object. Access is currently in beta.

    `sic_codes: list[str] | None`
    :   Define codes that categorize business activities

    `tags: list[str] | None`
    :   A list of tag values associated with the account (e.g. ['Enterprise', 'Tier 1']).

    `ticker_symbol: str | None`
    :   Define the ticker symbol

    `touched_at: str | None`
    :   The date and time the account was last touched.

    `updated_at: str | None`
    :   The type of the None singleton.

    `website_url: str | None`
    :   The type of the None singleton.

<a id="AccountLinks"></a>

`AccountLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="AccountResponse"></a>

`AccountResponse(**data: Any)`
:   AccountResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Account | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountsList"></a>

`AccountsList(**data: Any)`
:   AccountsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Account] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountsListResultMeta"></a>

`AccountsListResultMeta(**data: Any)`
:   Metadata for accounts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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
    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AccountsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

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

`AirbyteSearchResult[CallDispositionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[CallPurposesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[CallsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MailboxesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MailingsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[OpportunitiesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[PersonasSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[ProspectsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[SequenceStatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[SequenceStepsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[SequencesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[SnippetsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[StagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[TasksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[TemplatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

<a id="Call"></a>

`Call(**data: Any)`
:   Outreach call object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.CallAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.CallLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="CallAttributes"></a>

`CallAttributes(**data: Any)`
:   Nested schema for Call.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answered_at: str | None`
    :   The type of the None singleton.

    `completed_at: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `dialed_at: str | None`
    :   The type of the None singleton.

    `direction: str | None`
    :   The type of the None singleton.

    `external_vendor: str | None`
    :   The voice provider of the call. Can be blank.

    `from_: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `outcome: str | None`
    :   The type of the None singleton.

    `recording_url: str | None`
    :   The URL of the call's audio recording. This field only accepts HTTP and HTTPS values.

    `returned_at: str | None`
    :   The date and time the call was returned.

    `sequence_action: str | None`
    :   The action to take on the associated sequence; must be either 'Advance', 'Finish', 'Finish - No Reply', or 'Finish - Replied'.

    `should_record_call: bool | None`
    :   Indicated whether or not the call is recorded.

    `state: str | None`
    :   The type of the None singleton.

    `state_changed_at: str | None`
    :   The date and time the call’s state last changed.

    `tags: list[str] | None`
    :   A list of tag values associated with the call (e.g. ['Interested', 'Meeting Booked']).

    `to: str | None`
    :   The type of the None singleton.

    `uid: str | None`
    :   The Outreach voice trace id.

    `updated_at: str | None`
    :   The type of the None singleton.

    `user_call_type: str | None`
    :   The type of call placed within the Outreach client; must be either 'bridge' or 'voip'.

    `vendor_call_id: str | None`
    :   The call-id as recorded by the voice provider. Can be blank.

    `voicemail_recording_url: str | None`
    :   The URL of the call’s voicemail audio recording.

<a id="CallDisposition"></a>

`CallDisposition(**data: Any)`
:   Outreach call disposition object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.CallDispositionAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.CallDispositionLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="CallDispositionAttributes"></a>

`CallDispositionAttributes(**data: Any)`
:   Nested schema for CallDisposition.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `default_for_outbound_voicemail: bool | None`
    :   Default for outbound voicemail

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `order: int | None`
    :   The type of the None singleton.

    `outcome: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="CallDispositionLinks"></a>

`CallDispositionLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="CallDispositionResponse"></a>

`CallDispositionResponse(**data: Any)`
:   CallDispositionResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.CallDisposition | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CallDispositionsList"></a>

`CallDispositionsList(**data: Any)`
:   CallDispositionsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.CallDisposition] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CallDispositionsListResultMeta"></a>

`CallDispositionsListResultMeta(**data: Any)`
:   Metadata for call_dispositions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="CallLinks"></a>

`CallLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="CallPurpose"></a>

`CallPurpose(**data: Any)`
:   Outreach call purpose object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.CallPurposeAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.CallPurposeLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="CallPurposeAttributes"></a>

`CallPurposeAttributes(**data: Any)`
:   Nested schema for CallPurpose.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `order: int | None`
    :   The purpose’s display order within the collection.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="CallPurposeLinks"></a>

`CallPurposeLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="CallPurposeResponse"></a>

`CallPurposeResponse(**data: Any)`
:   CallPurposeResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.CallPurpose | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CallPurposesList"></a>

`CallPurposesList(**data: Any)`
:   CallPurposesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.CallPurpose] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CallPurposesListResultMeta"></a>

`CallPurposesListResultMeta(**data: Any)`
:   Metadata for call_purposes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="CallResponse"></a>

`CallResponse(**data: Any)`
:   CallResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Call | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CallsList"></a>

`CallsList(**data: Any)`
:   CallsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Call] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CallsListResultMeta"></a>

`CallsListResultMeta(**data: Any)`
:   Metadata for calls.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="JsonApiResource"></a>

`JsonApiResource(**data: Any)`
:   JsonApiResource type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="Mailbox"></a>

`Mailbox(**data: Any)`
:   Outreach mailbox object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.MailboxAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.MailboxLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="MailboxAttributes"></a>

`MailboxAttributes(**data: Any)`
:   Nested schema for Mailbox.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auth_id: int | None`
    :   The auth id associated with the mailbox.

    `created_at: str | None`
    :   The type of the None singleton.

    `editable: bool | None`
    :   A boolean value to indicate if the user has the permission to edit mailbox fields.

    `email: str | None`
    :   The type of the None singleton.

    `email_hash: str | None`
    :   Hashed email address of the mailbox.

    `email_provider: str | None`
    :   The mail service provider. While not a required field, it is strongly recommended to use one of 'exchange_online', 'exchange_server', 'gmail', 'gmail_api', 'google_oauth2', 'intermedia', 'office365_oauth2', 'microsoft_hma_oauth2', 'office_365', 'rackspace'. If no value is provided, send and sync will make assumptions based on the ews, imap, and smtp values provided.

    `email_signature: str | None`
    :   The default signature, in HTML, to be appended to sent email messages.

    `ews_custom_search_folder: bool | None`
    :   EWS custom search folder

    `ews_delegate_sync: bool | None`
    :   EWS delegate sync

    `ews_endpoint: str | None`
    :   The url of the Exchange Web Service.

    `ews_impersonation: bool | None`
    :   EWS impersonation

    `ews_ssl_verify_mode: int | None`
    :   The SSL verify mode, represented as an integer, the EWS connection will used. (verify none=0, verify peer=1, verify client once=4, verify fail if no peer cert=2)

    `exchange_version: str | None`
    :   The version of Exchange. Must be one of 'Exchange2007', 'Exchange2007_SP1', 'Exchange2010', 'Exchange2010_SP1', 'Exchange2010_SP2', 'Exchange2013', 'Exchange2013_SP1'.

    `imap_host: str | None`
    :   The address of the IMAP host, used for syncing (e.g. 'imap.gmail.com').

    `imap_port: int | None`
    :   The port number the IMAP server is using (e.g. '993').

    `imap_ssl: bool | None`
    :   A boolean value whether the IMAP connection will use SSL.

    `max_emails_per_day: int | None`
    :   The maximum number of in/out emails per day.

    `max_mailings_per_day: int | None`
    :   The maximum number of emails the application can send in a day from this mailbox. Recommended value is 500.

    `max_mailings_per_week: int | None`
    :   The maximum number of emails the application can send within a week from this mailbox. Recommended value is 5000.

    `model_config`
    :   The type of the None singleton.

    `opt_out_message: str | None`
    :   The message displayed on the unsubscribe confirmation page, seen after clicking the unsubscribe link in the email (e.g. 'To unsubscribe, click the button below.').

    `opt_out_signature: str | None`
    :   The message below the signature, in HTML, when the sequence requires an unsubscribe link (e.g. 'If you'd like me to stop sending you emails, please ` click here `').

    `prospect_email_exclusions: str | None`
    :   A list (provided as a string, newline-delimited) of email address patterns to be excluded from syncing (e.g. '`*@outreach.io daniel@example.com`').

    `provider_id: int | None`
    :   The id of the provider associated with this calendar.

    `provider_type: str | None`
    :   Email provider type.

    `send_disabled: bool | None`
    :   A boolean value whether sending is disabled from this mailbox.

    `send_errored_at: str | None`
    :   The date and time the most recent send error occurred.

    `send_max_retries: int | None`
    :   The maximum number of times to auto-retry a delivery when it fails.

    `send_method: str | None`
    :   The method used for sending email. Must be either 'ews', 'sendgrid', or 'smtp'.

    `send_period: int | None`
    :   The amount of time in seconds that the number of sendThreshold emails can be sent. Recommended value is two deliveries per minute (sendPeriod is 60).

    `send_permanent_error_at: str | None`
    :   Send permanent error at

    `send_requires_sync: bool | None`
    :   A boolean value whether the mailbox is required to be recently synced before sending.

    `send_state: str | None`
    :   Send state

    `send_success_at: str | None`
    :   The date and time the most recent successful email send occurred.

    `send_threshold: int | None`
    :   The maximum number of email sends per the sendPeriod amount of time. Recommended value is two deliveries per minute (sendThreshold is 2).

    `sendgrid_webhook_url: str | None`
    :   The endpoint required within the SendGrid account settings to support bounce and spam-report tracking.

    `smtp_host: str | None`
    :   The address of the SMTP host, used for sending (e.g. 'smtp.gmail.com').

    `smtp_port: int | None`
    :   The port number the SMTP server is using (e.g. '587').

    `smtp_ssl: bool | None`
    :   A boolean value whether the SMTP connection will use SSL.

    `smtp_username: str | None`
    :   The username for the SMTP account. This value should be left blank unless a separate SMTP account is being used for sending (i.e. not the mailbox's main username/password).

    `sync_active_frequency: int | None`
    :   The amount of time in seconds between syncing when the user is actively using the application.

    `sync_disabled: bool | None`
    :   A boolean value whether syncing is disabled from this mailbox.

    `sync_errored_at: str | None`
    :   The date and time the most recent sync error occurred.

    `sync_finished_at: str | None`
    :   The date and time the most recent sync finished.

    `sync_method: str | None`
    :   The method used for syncing email. Must be either 'ews', 'gmail_api', or 'imap'.

    `sync_outreach_folder: bool | None`
    :   A boolean value whether the folder for syncing is named 'Outreach' instead of 'Inbox'. Only available for Exchange version 'Exchange2007_SP1'.

    `sync_passive_frequency: int | None`
    :   The amount of time in seconds between syncing when the user is not actively using the application.

    `sync_state: str | None`
    :   Sync state

    `sync_success_at: str | None`
    :   The date and time the most recent successful email sync occurred.

    `updated_at: str | None`
    :   The type of the None singleton.

    `user_id: int | None`
    :   The id of the user associated with this mailbox.

    `username: str | None`
    :   The username of the email account. While not a required field, a username is necessary for most email providers outside of OAuth. This value is normally the same as the email address.

<a id="MailboxLinks"></a>

`MailboxLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="MailboxResponse"></a>

`MailboxResponse(**data: Any)`
:   MailboxResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Mailbox | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MailboxesList"></a>

`MailboxesList(**data: Any)`
:   MailboxesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Mailbox] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MailboxesListResultMeta"></a>

`MailboxesListResultMeta(**data: Any)`
:   Metadata for mailboxes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="Mailing"></a>

`Mailing(**data: Any)`
:   Outreach mailing object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.MailingAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.MailingLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="MailingAttributes"></a>

`MailingAttributes(**data: Any)`
:   Nested schema for Mailing.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body_html: str | None`
    :   The type of the None singleton.

    `body_text: str | None`
    :   The plain-text representation of the 'bodyHTML' field.

    `bounced_at: str | None`
    :   The date and time the email was bounced.

    `classification: list[typing.Any] | None`
    :   Classification

    `click_count: int | None`
    :   The total number of times links within the email were clicked (if the message is tracking links).

    `clicked_at: str | None`
    :   The most recent date and time a link was clicked (if the message is tracking links).

    `created_at: str | None`
    :   The type of the None singleton.

    `delivered_at: str | None`
    :   The date and time the email was delivered.

    `error_backtrace: str | None`
    :   Technical details explaining the mailing's error.

    `error_reason: str | None`
    :   A summary explaining the mailing's error.

    `follow_up_task_scheduled_at: str | None`
    :   The date and time of when a follow-up task should be due for this mailing.

    `follow_up_task_type: str | None`
    :   The type of follow-up task to create. Possible values are 'follow_up' or 'no_reply'.

    `mailbox_address: str | None`
    :   The email address the mailing was sent from.

    `mailing_type: str | None`
    :   The type of the None singleton.

    `marked_as_spam_at: str | None`
    :   The date and time the email was marked as spam.

    `message_id: str | None`
    :   The MIME content Message-ID of the delivered message.

    `model_config`
    :   The type of the None singleton.

    `notify_thread_condition: str | None`
    :   The condition of when to bump this mailing to the top of the user's inbox. Possible values are 'always' or 'no_reply'.

    `notify_thread_scheduled_at: str | None`
    :   The date and time of when this mailing should be bumped to the top of the user's inbox.

    `notify_thread_status: str | None`
    :   The status of the bump. Possible values are 'pending', 'sent' or 'skipped'.

    `open_count: int | None`
    :   The total number of times the email was opened (if the message is tracking opens).

    `opened_at: str | None`
    :   The most recent date and time the email was opened (if the message is tracking opens).

    `override_safety_settings: bool | None`
    :   A boolean value whether users can override submission if template variables have not all been replaced.

    `references: list[str] | None`
    :   A list of references for the mailing taken from the email header.

    `replied_at: str | None`
    :   The date and time the email was replied to.

    `retry_at: str | None`
    :   The date and time the email will rety to send.

    `retry_count: int | None`
    :   The number of times the email has been retried to send.

    `retry_interval: int | None`
    :   The amount of time in seconds between retry attempts.

    `scheduled_at: str | None`
    :   The date and time the email is scheduled to send.

    `state: str | None`
    :   The type of the None singleton.

    `state_changed_at: str | None`
    :   The date and time the state last changed.

    `subject: str | None`
    :   The type of the None singleton.

    `track_links: bool | None`
    :   A boolean value whether the mailing is tracking link clicks.

    `track_opens: bool | None`
    :   A boolean value whether the mailing is tracking email opens.

    `unsubscribed_at: str | None`
    :   The date and time the recepient unsubscribed from the mailing's sequence.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="MailingLinks"></a>

`MailingLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="MailingResponse"></a>

`MailingResponse(**data: Any)`
:   MailingResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Mailing | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MailingsList"></a>

`MailingsList(**data: Any)`
:   MailingsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Mailing] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MailingsListResultMeta"></a>

`MailingsListResultMeta(**data: Any)`
:   Metadata for mailings.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="OpportunitiesList"></a>

`OpportunitiesList(**data: Any)`
:   OpportunitiesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Opportunity] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OpportunitiesListResultMeta"></a>

`OpportunitiesListResultMeta(**data: Any)`
:   Metadata for opportunities.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="Opportunity"></a>

`Opportunity(**data: Any)`
:   Outreach opportunity object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.OpportunityAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.OpportunityLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="OpportunityAttributes"></a>

`OpportunityAttributes(**data: Any)`
:   Nested schema for Opportunity.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: float | None`
    :   The type of the None singleton.

    `amount_precise: str | None`
    :   The precise amount that the opportunity is worth.

    `close_date: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `currency_type: str | None`
    :   The ISO code of the currency this opportunity is in.

    `custom1: str | None`
    :   The value of the opportunity's first custom field.

    `custom10: str | None`
    :   The value of the opportunity's 10th custom field.

    `custom100: str | None`
    :   The value of the opportunity's 100th custom field.

    `custom101: str | None`
    :   The value of the opportunity’s 101st custom field.

    `custom102: str | None`
    :   The value of the opportunity’s 102nd custom field.

    `custom103: str | None`
    :   The value of the opportunity’s 103rd custom field.

    `custom104: str | None`
    :   The value of the opportunity’s 104th custom field.

    `custom105: str | None`
    :   The value of the opportunity’s 105th custom field.

    `custom106: str | None`
    :   The value of the opportunity’s 106th custom field.

    `custom107: str | None`
    :   The value of the opportunity’s 107th custom field.

    `custom108: str | None`
    :   The value of the opportunity’s 108th custom field.

    `custom109: str | None`
    :   The value of the opportunity’s 109th custom field.

    `custom11: str | None`
    :   The value of the opportunity's 11th custom field.

    `custom110: str | None`
    :   The value of the opportunity’s 110th custom field.

    `custom111: str | None`
    :   The value of the opportunity’s 111th custom field.

    `custom112: str | None`
    :   The value of the opportunity’s 112th custom field.

    `custom113: str | None`
    :   The value of the opportunity’s 113th custom field.

    `custom114: str | None`
    :   The value of the opportunity’s 114th custom field.

    `custom115: str | None`
    :   The value of the opportunity’s 115th custom field.

    `custom116: str | None`
    :   The value of the opportunity’s 116th custom field.

    `custom117: str | None`
    :   The value of the opportunity’s 117th custom field.

    `custom118: str | None`
    :   The value of the opportunity’s 118th custom field.

    `custom119: str | None`
    :   The value of the opportunity’s 119th custom field.

    `custom12: str | None`
    :   The value of the opportunity's 12th custom field.

    `custom120: str | None`
    :   The value of the opportunity’s 120th custom field.

    `custom121: str | None`
    :   The value of the opportunity’s 121st custom field.

    `custom122: str | None`
    :   The value of the opportunity’s 122nd custom field.

    `custom123: str | None`
    :   The value of the opportunity’s 123rd custom field.

    `custom124: str | None`
    :   The value of the opportunity’s 124th custom field.

    `custom125: str | None`
    :   The value of the opportunity’s 125th custom field.

    `custom126: str | None`
    :   The value of the opportunity’s 126th custom field.

    `custom127: str | None`
    :   The value of the opportunity’s 127th custom field.

    `custom128: str | None`
    :   The value of the opportunity’s 128th custom field.

    `custom129: str | None`
    :   The value of the opportunity’s 129th custom field.

    `custom13: str | None`
    :   The value of the opportunity's 13th custom field.

    `custom130: str | None`
    :   The value of the opportunity’s 130th custom field.

    `custom131: str | None`
    :   The value of the opportunity’s 131st custom field.

    `custom132: str | None`
    :   The value of the opportunity’s 132nd custom field.

    `custom133: str | None`
    :   The value of the opportunity’s 133rd custom field.

    `custom134: str | None`
    :   The value of the opportunity’s 134th custom field.

    `custom135: str | None`
    :   The value of the opportunity’s 135th custom field.

    `custom136: str | None`
    :   The value of the opportunity’s 136th custom field.

    `custom137: str | None`
    :   The value of the opportunity’s 137th custom field.

    `custom138: str | None`
    :   The value of the opportunity’s 138th custom field.

    `custom139: str | None`
    :   The value of the opportunity’s 139th custom field.

    `custom14: str | None`
    :   The value of the opportunity's 14th custom field.

    `custom140: str | None`
    :   The value of the opportunity’s 140th custom field.

    `custom141: str | None`
    :   The value of the opportunity’s 141st custom field.

    `custom142: str | None`
    :   The value of the opportunity’s 142nd custom field.

    `custom143: str | None`
    :   The value of the opportunity’s 143rd custom field.

    `custom144: str | None`
    :   The value of the opportunity’s 144th custom field.

    `custom145: str | None`
    :   The value of the opportunity’s 145th custom field.

    `custom146: str | None`
    :   The value of the opportunity’s 146th custom field.

    `custom147: str | None`
    :   The value of the opportunity’s 147th custom field.

    `custom148: str | None`
    :   The value of the opportunity’s 148th custom field.

    `custom149: str | None`
    :   The value of the opportunity’s 149th custom field.

    `custom15: str | None`
    :   The value of the opportunity's 15th custom field.

    `custom150: str | None`
    :   The value of the opportunity’s 150th custom field.

    `custom16: str | None`
    :   The value of the opportunity's 16th custom field.

    `custom17: str | None`
    :   The value of the opportunity's 17th custom field.

    `custom18: str | None`
    :   The value of the opportunity's 18th custom field.

    `custom19: str | None`
    :   The value of the opportunity's 19th custom field.

    `custom2: str | None`
    :   The value of the opportunity's second custom field.

    `custom20: str | None`
    :   The value of the opportunity's 20th custom field.

    `custom21: str | None`
    :   The value of the opportunity's 21st custom field.

    `custom22: str | None`
    :   The value of the opportunity's 22nd custom field.

    `custom23: str | None`
    :   The value of the opportunity's 23rd custom field.

    `custom24: str | None`
    :   The value of the opportunity's 24th custom field.

    `custom25: str | None`
    :   The value of the opportunity's 25th custom field.

    `custom26: str | None`
    :   The value of the opportunity's 26th custom field.

    `custom27: str | None`
    :   The value of the opportunity's 27th custom field.

    `custom28: str | None`
    :   The value of the opportunity's 28th custom field.

    `custom29: str | None`
    :   The value of the opportunity's 29th custom field.

    `custom3: str | None`
    :   The value of the opportunity's third custom field.

    `custom30: str | None`
    :   The value of the opportunity's 30th custom field.

    `custom31: str | None`
    :   The value of the opportunity's 31st custom field.

    `custom32: str | None`
    :   The value of the opportunity's 32nd custom field.

    `custom33: str | None`
    :   The value of the opportunity's 33rd custom field.

    `custom34: str | None`
    :   The value of the opportunity's 34th custom field.

    `custom35: str | None`
    :   The value of the opportunity's 35th custom field.

    `custom36: str | None`
    :   The value of the opportunity's 36th custom field.

    `custom37: str | None`
    :   The value of the opportunity's 37th custom field.

    `custom38: str | None`
    :   The value of the opportunity's 38th custom field.

    `custom39: str | None`
    :   The value of the opportunity's 39th custom field.

    `custom4: str | None`
    :   The value of the opportunity's fourth custom field.

    `custom40: str | None`
    :   The value of the opportunity's 40th custom field.

    `custom41: str | None`
    :   The value of the opportunity's 41st custom field.

    `custom42: str | None`
    :   The value of the opportunity's 42nd custom field.

    `custom43: str | None`
    :   The value of the opportunity's 43rd custom field.

    `custom44: str | None`
    :   The value of the opportunity's 44th custom field.

    `custom45: str | None`
    :   The value of the opportunity's 45th custom field.

    `custom46: str | None`
    :   The value of the opportunity's 46th custom field.

    `custom47: str | None`
    :   The value of the opportunity's 47th custom field.

    `custom48: str | None`
    :   The value of the opportunity's 48th custom field.

    `custom49: str | None`
    :   The value of the opportunity's 49th custom field.

    `custom5: str | None`
    :   The value of the opportunity's fifth custom field.

    `custom50: str | None`
    :   The value of the opportunity's 50th custom field.

    `custom51: str | None`
    :   The value of the opportunity's 51st custom field.

    `custom52: str | None`
    :   The value of the opportunity's 52nd custom field.

    `custom53: str | None`
    :   The value of the opportunity's 53rd custom field.

    `custom54: str | None`
    :   The value of the opportunity's 54th custom field.

    `custom55: str | None`
    :   The value of the opportunity's 55th custom field.

    `custom56: str | None`
    :   The value of the opportunity's 56th custom field.

    `custom57: str | None`
    :   The value of the opportunity's 57th custom field.

    `custom58: str | None`
    :   The value of the opportunity's 58th custom field.

    `custom59: str | None`
    :   The value of the opportunity's 59th custom field.

    `custom6: str | None`
    :   The value of the opportunity's sixth custom field.

    `custom60: str | None`
    :   The value of the opportunity's 60th custom field.

    `custom61: str | None`
    :   The value of the opportunity's 61st custom field.

    `custom62: str | None`
    :   The value of the opportunity's 62nd custom field.

    `custom63: str | None`
    :   The value of the opportunity's 63rd custom field.

    `custom64: str | None`
    :   The value of the opportunity's 64th custom field.

    `custom65: str | None`
    :   The value of the opportunity's 65th custom field.

    `custom66: str | None`
    :   The value of the opportunity's 66th custom field.

    `custom67: str | None`
    :   The value of the opportunity's 67th custom field.

    `custom68: str | None`
    :   The value of the opportunity's 68th custom field.

    `custom69: str | None`
    :   The value of the opportunity's 69th custom field.

    `custom7: str | None`
    :   The value of the opportunity's seventh custom field.

    `custom70: str | None`
    :   The value of the opportunity's 70th custom field.

    `custom71: str | None`
    :   The value of the opportunity's 71st custom field.

    `custom72: str | None`
    :   The value of the opportunity's 72nd custom field.

    `custom73: str | None`
    :   The value of the opportunity's 73rd custom field.

    `custom74: str | None`
    :   The value of the opportunity's 74th custom field.

    `custom75: str | None`
    :   The value of the opportunity's 75th custom field.

    `custom76: str | None`
    :   The value of the opportunity's 76th custom field.

    `custom77: str | None`
    :   The value of the opportunity's 77th custom field.

    `custom78: str | None`
    :   The value of the opportunity's 78th custom field.

    `custom79: str | None`
    :   The value of the opportunity's 79th custom field.

    `custom8: str | None`
    :   The value of the opportunity's eighth custom field.

    `custom80: str | None`
    :   The value of the opportunity's 80th custom field.

    `custom81: str | None`
    :   The value of the opportunity's 81st custom field.

    `custom82: str | None`
    :   The value of the opportunity's 82nd custom field.

    `custom83: str | None`
    :   The value of the opportunity's 83rd custom field.

    `custom84: str | None`
    :   The value of the opportunity's 84th custom field.

    `custom85: str | None`
    :   The value of the opportunity's 85th custom field.

    `custom86: str | None`
    :   The value of the opportunity's 86th custom field.

    `custom87: str | None`
    :   The value of the opportunity's 87th custom field.

    `custom88: str | None`
    :   The value of the opportunity's 88th custom field.

    `custom89: str | None`
    :   The value of the opportunity's 89th custom field.

    `custom9: str | None`
    :   The value of the opportunity's ninth custom field.

    `custom90: str | None`
    :   The value of the opportunity's 90th custom field.

    `custom91: str | None`
    :   The value of the opportunity's 91st custom field.

    `custom92: str | None`
    :   The value of the opportunity's 92nd custom field.

    `custom93: str | None`
    :   The value of the opportunity's 93rd custom field.

    `custom94: str | None`
    :   The value of the opportunity's 94th custom field.

    `custom95: str | None`
    :   The value of the opportunity's 95th custom field.

    `custom96: str | None`
    :   The value of the opportunity's 96th custom field.

    `custom97: str | None`
    :   The value of the opportunity's 97th custom field.

    `custom98: str | None`
    :   The value of the opportunity's 98th custom field.

    `custom99: str | None`
    :   The value of the opportunity's 99th custom field.

    `custom_id: str | None`
    :   A custom ID for the opportunity, often referencing an ID in an external system.

    `description: str | None`
    :   A description of the opportunity.

    `external_created_at: str | None`
    :   The date the opportunity was created in the external system.

    `external_updated_at: str | None`
    :   The date the opportunity was last updated in the external system.

    `forecast_category: str | None`
    :   The category or classification used to predict the likelihood of closing an opportunity.

    `health_category: str | None`
    :   Health category

    `health_score: int | None`
    :   Health score

    `lead_source: str | None`
    :   Source of this opportunity, such as Advertisement or Trade Show

    `lost_reason: str | None`
    :   The reason why an opportunity or deal was lost.

    `map_link: str | None`
    :   A link to the SamePlan MAP (Mutual Action Plan) associated with this opportunity.

    `map_next_steps: str | None`
    :   The next event in the timeline that has yet to be completed for the SamePlan MAP (Mutual Action Plan).

    `map_number_of_overdue_tasks: int | None`
    :   Map number of overdue tasks

    `map_status: str | None`
    :   The status of the SamePlan MAP (Mutual Action Plan) based on how well both parties are trending towards the plan.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `next_step: str | None`
    :   The next step to take for the opportunity.

    `opportunity_type: str | None`
    :   The type of opportunity.

    `probability: int | None`
    :   The type of the None singleton.

    `prospecting_rep_id: str | None`
    :   The ID of the sales rep that prospects the opportunity.

    `record_type: str | None`
    :   The type or category of the record, such as Opportunity, Lead, or Deal, used to classify and organize different stages in the sales process

    `sharing_team_id: str | None`
    :   The ID of the sharing team associated with this object. Access is currently in beta.

    `state: str | None`
    :   State

    `tags: list[str] | None`
    :   Tags associated with the opportunity.

    `touched_at: str | None`
    :   The last time an event happened for an opportunity.

    `trashed_at: str | None`
    :   The date a prospect was soft deleted.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="OpportunityLinks"></a>

`OpportunityLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="OpportunityResponse"></a>

`OpportunityResponse(**data: Any)`
:   OpportunityResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Opportunity | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

<a id="OutreachCheckResult"></a>

`OutreachCheckResult(**data: Any)`
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

<a id="OutreachExecuteResult"></a>

`OutreachExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="OutreachExecuteResultWithMeta"></a>

`OutreachExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Account], AccountsListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[CallDisposition], CallDispositionsListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[CallPurpose], CallPurposesListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Call], CallsListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Mailbox], MailboxesListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Mailing], MailingsListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Opportunity], OpportunitiesListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Persona], PersonasListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Prospect], ProspectsListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[SequenceState], SequenceStatesListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[SequenceStep], SequenceStepsListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Sequence], SequencesListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Snippet], SnippetsListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Stage], StagesListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Task], TasksListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Template], TemplatesListResultMeta]
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`OutreachExecuteResultWithMeta[list[Account], AccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountsListResult"></a>

`AccountsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[CallDisposition], CallDispositionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CallDispositionsListResult"></a>

`CallDispositionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[CallPurpose], CallPurposesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CallPurposesListResult"></a>

`CallPurposesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Call], CallsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CallsListResult"></a>

`CallsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Mailbox], MailboxesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MailboxesListResult"></a>

`MailboxesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Mailing], MailingsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MailingsListResult"></a>

`MailingsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Opportunity], OpportunitiesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OpportunitiesListResult"></a>

`OpportunitiesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Persona], PersonasListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PersonasListResult"></a>

`PersonasListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Prospect], ProspectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProspectsListResult"></a>

`ProspectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[SequenceState], SequenceStatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SequenceStatesListResult"></a>

`SequenceStatesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[SequenceStep], SequenceStepsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SequenceStepsListResult"></a>

`SequenceStepsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Sequence], SequencesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SequencesListResult"></a>

`SequencesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Snippet], SnippetsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SnippetsListResult"></a>

`SnippetsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Stage], StagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="StagesListResult"></a>

`StagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Task], TasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TasksListResult"></a>

`TasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[Template], TemplatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TemplatesListResult"></a>

`TemplatesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OutreachExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersListResult"></a>

`UsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

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

<a id="PaginationLinks"></a>

`PaginationLinks(**data: Any)`
:   PaginationLinks type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

    `prev: str | None`
    :   The type of the None singleton.

<a id="Persona"></a>

`Persona(**data: Any)`
:   Outreach persona object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.PersonaAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PersonaLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="PersonaAttributes"></a>

`PersonaAttributes(**data: Any)`
:   Nested schema for Persona.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   A description of the persona.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="PersonaLinks"></a>

`PersonaLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="PersonaResponse"></a>

`PersonaResponse(**data: Any)`
:   PersonaResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Persona | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PersonasList"></a>

`PersonasList(**data: Any)`
:   PersonasList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Persona] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PersonasListResultMeta"></a>

`PersonasListResultMeta(**data: Any)`
:   Metadata for personas.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="Prospect"></a>

`Prospect(**data: Any)`
:   Outreach prospect (contact) object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.ProspectAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.ProspectLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="ProspectAttributes"></a>

`ProspectAttributes(**data: Any)`
:   Nested schema for Prospect.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_name: str | None`
    :   Account name

    `added_at: str | None`
    :   The date and time the prospect was added to any system.

    `address_city: str | None`
    :   The prospect’s city (e.g. 'Seattle').

    `address_country: str | None`
    :   The prospect’s country (e.g. 'USA').

    `address_state: str | None`
    :   The prospect’s state (e.g. 'Washington').

    `address_street: str | None`
    :   The prospect’s street address (e.g. '1441 N 34th St').

    `address_street2: str | None`
    :   The prospect’s second street address, if applicable.

    `address_zip: str | None`
    :   The prospect’s postal code (e.g. '98103').

    `angel_list_url: str | None`
    :   The prospect’s AngelList URL.

    `available_at: str | None`
    :   The date and time the prospect is available to contact again.

    `call_opted_out: bool | None`
    :   Whether the prospect is opted out of calling, or opted out in general if granular opt-out is not enabled.

    `calls_opt_status: str | None`
    :   A string ('opted_in', 'opted_out', 'null') that represents whether a prospect has opted into or out of calls.

    `calls_opted_at: str | None`
    :   The date and time the prospect opted in/out of calls.

    `campaign_name: str | None`
    :   The name of the campaign the prospect is associated with.

    `click_count: int | None`
    :   The number of clicks the prospect has made since the last touch point.

    `company: str | None`
    :   The type of the None singleton.

    `company_industry: str | None`
    :   Company industry

    `company_natural: str | None`
    :   Company natural

    `company_size: int | None`
    :   Company size

    `company_type: str | None`
    :   Company type

    `contact_histogram: list[typing.Any] | None`
    :   The last 12 months of email contact history with the prospect, with the current month being the last element. The format for each month is '[inboundCount, outboundCount]'. Note: Retrieving this field will slow down the queries. Unless this field is required, it is best to filter it out. See Specify Sparse Fieldsets for examples

    `created_at: str | None`
    :   The type of the None singleton.

    `custom1: str | None`
    :   The value of the prospect’s first custom field.

    `custom10: str | None`
    :   The value of the prospect’s 10th custom field.

    `custom100: str | None`
    :   The value of the prospect’s 100th custom field.

    `custom101: str | None`
    :   The value of the prospect’s 101st custom field.

    `custom102: str | None`
    :   The value of the prospect’s 102nd custom field.

    `custom103: str | None`
    :   The value of the prospect’s 103rd custom field.

    `custom104: str | None`
    :   The value of the prospect’s 104th custom field.

    `custom105: str | None`
    :   The value of the prospect’s 105th custom field.

    `custom106: str | None`
    :   The value of the prospect’s 106th custom field.

    `custom107: str | None`
    :   The value of the prospect’s 107th custom field.

    `custom108: str | None`
    :   The value of the prospect’s 108th custom field.

    `custom109: str | None`
    :   The value of the prospect’s 109th custom field.

    `custom11: str | None`
    :   The value of the prospect’s 11th custom field.

    `custom110: str | None`
    :   The value of the prospect’s 110th custom field.

    `custom111: str | None`
    :   The value of the prospect’s 111th custom field.

    `custom112: str | None`
    :   The value of the prospect’s 112th custom field.

    `custom113: str | None`
    :   The value of the prospect’s 113th custom field.

    `custom114: str | None`
    :   The value of the prospect’s 114th custom field.

    `custom115: str | None`
    :   The value of the prospect’s 115th custom field.

    `custom116: str | None`
    :   The value of the prospect’s 116th custom field.

    `custom117: str | None`
    :   The value of the prospect’s 117th custom field.

    `custom118: str | None`
    :   The value of the prospect’s 118th custom field.

    `custom119: str | None`
    :   The value of the prospect’s 119th custom field.

    `custom12: str | None`
    :   The value of the prospect’s 12th custom field.

    `custom120: str | None`
    :   The value of the prospect’s 120th custom field.

    `custom121: str | None`
    :   The value of the prospect’s 121st custom field.

    `custom122: str | None`
    :   The value of the prospect’s 122nd custom field.

    `custom123: str | None`
    :   The value of the prospect’s 123rd custom field.

    `custom124: str | None`
    :   The value of the prospect’s 124th custom field.

    `custom125: str | None`
    :   The value of the prospect’s 125th custom field.

    `custom126: str | None`
    :   The value of the prospect’s 126th custom field.

    `custom127: str | None`
    :   The value of the prospect’s 127th custom field.

    `custom128: str | None`
    :   The value of the prospect’s 128th custom field.

    `custom129: str | None`
    :   The value of the prospect’s 129th custom field.

    `custom13: str | None`
    :   The value of the prospect’s 13th custom field.

    `custom130: str | None`
    :   The value of the prospect’s 130th custom field.

    `custom131: str | None`
    :   The value of the prospect’s 131st custom field.

    `custom132: str | None`
    :   The value of the prospect’s 132nd custom field.

    `custom133: str | None`
    :   The value of the prospect’s 133rd custom field.

    `custom134: str | None`
    :   The value of the prospect’s 134th custom field.

    `custom135: str | None`
    :   The value of the prospect’s 135th custom field.

    `custom136: str | None`
    :   The value of the prospect’s 136th custom field.

    `custom137: str | None`
    :   The value of the prospect’s 137th custom field.

    `custom138: str | None`
    :   The value of the prospect’s 138th custom field.

    `custom139: str | None`
    :   The value of the prospect’s 139th custom field.

    `custom14: str | None`
    :   The value of the prospect’s 14th custom field.

    `custom140: str | None`
    :   The value of the prospect’s 140th custom field.

    `custom141: str | None`
    :   The value of the prospect’s 141st custom field.

    `custom142: str | None`
    :   The value of the prospect’s 142nd custom field.

    `custom143: str | None`
    :   The value of the prospect’s 143rd custom field.

    `custom144: str | None`
    :   The value of the prospect’s 144th custom field.

    `custom145: str | None`
    :   The value of the prospect’s 145th custom field.

    `custom146: str | None`
    :   The value of the prospect’s 146th custom field.

    `custom147: str | None`
    :   The value of the prospect’s 147th custom field.

    `custom148: str | None`
    :   The value of the prospect’s 148th custom field.

    `custom149: str | None`
    :   The value of the prospect’s 149th custom field.

    `custom15: str | None`
    :   The value of the prospect’s 15th custom field.

    `custom150: str | None`
    :   The value of the prospect’s 150th custom field.

    `custom16: str | None`
    :   The value of the prospect’s 16th custom field.

    `custom17: str | None`
    :   The value of the prospect’s 17th custom field.

    `custom18: str | None`
    :   The value of the prospect’s 18th custom field.

    `custom19: str | None`
    :   The value of the prospect’s 19th custom field.

    `custom2: str | None`
    :   The value of the prospect’s second custom field.

    `custom20: str | None`
    :   The value of the prospect’s 20th custom field.

    `custom21: str | None`
    :   The value of the prospect’s 21st custom field.

    `custom22: str | None`
    :   The value of the prospect’s 22nd custom field.

    `custom23: str | None`
    :   The value of the prospect’s 23rd custom field.

    `custom24: str | None`
    :   The value of the prospect’s 24th custom field.

    `custom25: str | None`
    :   The value of the prospect’s 25th custom field.

    `custom26: str | None`
    :   The value of the prospect’s 26th custom field.

    `custom27: str | None`
    :   The value of the prospect’s 27th custom field.

    `custom28: str | None`
    :   The value of the prospect’s 28th custom field.

    `custom29: str | None`
    :   The value of the prospect’s 29th custom field.

    `custom3: str | None`
    :   The value of the prospect’s third custom field.

    `custom30: str | None`
    :   The value of the prospect’s 30th custom field.

    `custom31: str | None`
    :   The value of the prospect’s 31st custom field.

    `custom32: str | None`
    :   The value of the prospect’s 32nd custom field.

    `custom33: str | None`
    :   The value of the prospect’s 33rd custom field.

    `custom34: str | None`
    :   The value of the prospect’s 34th custom field.

    `custom35: str | None`
    :   The value of the prospect’s 35th custom field.

    `custom36: str | None`
    :   The value of the prospect’s 36th custom field.

    `custom37: str | None`
    :   The value of the prospect’s 37th custom field.

    `custom38: str | None`
    :   The value of the prospect’s 38th custom field.

    `custom39: str | None`
    :   The value of the prospect’s 39th custom field.

    `custom4: str | None`
    :   The value of the prospect’s fourth custom field.

    `custom40: str | None`
    :   The value of the prospect’s 40th custom field.

    `custom41: str | None`
    :   The value of the prospect’s 41st custom field.

    `custom42: str | None`
    :   The value of the prospect’s 42nd custom field.

    `custom43: str | None`
    :   The value of the prospect’s 43rd custom field.

    `custom44: str | None`
    :   The value of the prospect’s 44th custom field.

    `custom45: str | None`
    :   The value of the prospect’s 45th custom field.

    `custom46: str | None`
    :   The value of the prospect’s 46th custom field.

    `custom47: str | None`
    :   The value of the prospect’s 47th custom field.

    `custom48: str | None`
    :   The value of the prospect’s 48th custom field.

    `custom49: str | None`
    :   The value of the prospect’s 49th custom field.

    `custom5: str | None`
    :   The value of the prospect’s fifth custom field.

    `custom50: str | None`
    :   The value of the prospect’s 50th custom field.

    `custom51: str | None`
    :   The value of the prospect’s 51st custom field.

    `custom52: str | None`
    :   The value of the prospect’s 52nd custom field.

    `custom53: str | None`
    :   The value of the prospect’s 53rd custom field.

    `custom54: str | None`
    :   The value of the prospect’s 54th custom field.

    `custom55: str | None`
    :   The value of the prospect’s 55th custom field.

    `custom56: str | None`
    :   The value of the prospect’s 56th custom field.

    `custom57: str | None`
    :   The value of the prospect’s 57th custom field.

    `custom58: str | None`
    :   The value of the prospect’s 58th custom field.

    `custom59: str | None`
    :   The value of the prospect’s 59th custom field.

    `custom6: str | None`
    :   The value of the prospect’s sixth custom field.

    `custom60: str | None`
    :   The value of the prospect’s 60th custom field.

    `custom61: str | None`
    :   The value of the prospect’s 61st custom field.

    `custom62: str | None`
    :   The value of the prospect’s 62nd custom field.

    `custom63: str | None`
    :   The value of the prospect’s 63rd custom field.

    `custom64: str | None`
    :   The value of the prospect’s 64th custom field.

    `custom65: str | None`
    :   The value of the prospect’s 65th custom field.

    `custom66: str | None`
    :   The value of the prospect’s 66th custom field.

    `custom67: str | None`
    :   The value of the prospect’s 67th custom field.

    `custom68: str | None`
    :   The value of the prospect’s 68th custom field.

    `custom69: str | None`
    :   The value of the prospect’s 69th custom field.

    `custom7: str | None`
    :   The value of the prospect’s seventh custom field.

    `custom70: str | None`
    :   The value of the prospect’s 70th custom field.

    `custom71: str | None`
    :   The value of the prospect’s 71st custom field.

    `custom72: str | None`
    :   The value of the prospect’s 72nd custom field.

    `custom73: str | None`
    :   The value of the prospect’s 73rd custom field.

    `custom74: str | None`
    :   The value of the prospect’s 74th custom field.

    `custom75: str | None`
    :   The value of the prospect’s 75th custom field.

    `custom76: str | None`
    :   The value of the prospect’s 76th custom field.

    `custom77: str | None`
    :   The value of the prospect’s 77th custom field.

    `custom78: str | None`
    :   The value of the prospect’s 78th custom field.

    `custom79: str | None`
    :   The value of the prospect’s 79th custom field.

    `custom8: str | None`
    :   The value of the prospect’s eight custom field.

    `custom80: str | None`
    :   The value of the prospect’s 80th custom field.

    `custom81: str | None`
    :   The value of the prospect’s 81st custom field.

    `custom82: str | None`
    :   The value of the prospect’s 82nd custom field.

    `custom83: str | None`
    :   The value of the prospect’s 83rd custom field.

    `custom84: str | None`
    :   The value of the prospect’s 84th custom field.

    `custom85: str | None`
    :   The value of the prospect’s 85th custom field.

    `custom86: str | None`
    :   The value of the prospect’s 86th custom field.

    `custom87: str | None`
    :   The value of the prospect’s 87th custom field.

    `custom88: str | None`
    :   The value of the prospect’s 88th custom field.

    `custom89: str | None`
    :   The value of the prospect’s 89th custom field.

    `custom9: str | None`
    :   The value of the prospect’s ninth custom field.

    `custom90: str | None`
    :   The value of the prospect’s 90th custom field.

    `custom91: str | None`
    :   The value of the prospect’s 91st custom field.

    `custom92: str | None`
    :   The value of the prospect’s 92nd custom field.

    `custom93: str | None`
    :   The value of the prospect’s 93rd custom field.

    `custom94: str | None`
    :   The value of the prospect’s 94th custom field.

    `custom95: str | None`
    :   The value of the prospect’s 95th custom field.

    `custom96: str | None`
    :   The value of the prospect’s 96th custom field.

    `custom97: str | None`
    :   The value of the prospect’s 97th custom field.

    `custom98: str | None`
    :   The value of the prospect’s 98th custom field.

    `custom99: str | None`
    :   The value of the prospect’s 99th custom field.

    `date_of_birth: str | None`
    :   The date the prospect was born.

    `degree: str | None`
    :   The degree(s) the prospect has received.

    `email_contacts: list[typing.Any] | None`
    :   Email contacts

    `email_opted_out: bool | None`
    :   Whether the prospect is opted out of email, or opted out in general if granular opt-out is not enabled.

    `emails: list[str | None] | None`
    :   The type of the None singleton.

    `emails_opt_status: str | None`
    :   A string ('opted_in', 'opted_out', 'null') that represents whether a prospect has opted into or out of emails.

    `emails_opted_at: str | None`
    :   The date and time the prospect opted in/out of emails.

    `engaged_at: str | None`
    :   The date and time the prospect last engaged.

    `engaged_score: float | None`
    :   A number representing the quality of the lead, based on the number of the prospect’s opens, clicks and mailing replies.

    `enrichable: bool | None`
    :   Enrichable

    `event_name: str | None`
    :   The name of the event the prospect was met at.

    `external_id: str | None`
    :   A custom ID for the prospect, often referencing an ID in an external system.

    `external_owner: str | None`
    :   A custom owner for the prospect, often referencing an ownering in an external system.

    `external_source: str | None`
    :   The source of the resource’s creation (e.g. 'outreach-api').

    `facebook_url: str | None`
    :   The prospect’s Facebook URL.

    `first_name: str | None`
    :   The type of the None singleton.

    `gender: str | None`
    :   The gender of the prospect.

    `github_url: str | None`
    :   The prospect’s GitHub URL.

    `github_username: str | None`
    :   The prospect’s GitHub username.

    `google_plus_url: str | None`
    :   The prospect’s Google+ URL.

    `graduation_date: str | None`
    :   The graduation date of the prospect.

    `home_phones: list[str] | None`
    :   A list of home phone numbers associated with the prospect.

    `job_start_date: str | None`
    :   The starting date of the prospect’s current job.

    `last_name: str | None`
    :   The type of the None singleton.

    `linked_in_connections: int | None`
    :   The number of connections on the prospect’s LinkedIn profile.

    `linked_in_id: str | None`
    :   The prospect’s LinkedIn ID.

    `linked_in_slug: str | None`
    :   The prospect’s LinkedIn slug.

    `linked_in_url: str | None`
    :   The prospect’s LinkedIn URL.

    `middle_name: str | None`
    :   The middle name of the prospect.

    `mobile_phones: list[str] | None`
    :   A list of mobile phone numbers associated with the prospect.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The full name of the prospect.

    `nickname: str | None`
    :   The nickname of the prospect.

    `occupation: str | None`
    :   The occupation of the prospect (e.g. 'Purchasing Manager').

    `open_count: int | None`
    :   The number of opens the prospect has made since the last touch point.

    `opted_out: bool | None`
    :   A boolean value representing whether this prospect is currently opted out of all mailings. Set this value to true to opt out the prospect; the 'opted_out' timestamp will be updated to the time of the request. Set this value to false to revert the opt at and clear the opted out timestamp.

    `opted_out_at: str | None`
    :   The date and time the prospect opted out of emails.

    `other_phones: list[str] | None`
    :   A list of other phone numbers associated with the prospect.

    `personal_note1: str | None`
    :   A custom note field related to the prospect.

    `personal_note2: str | None`
    :   A second note field related to the prospect.

    `preferred_contact: str | None`
    :   The preferred contact method for the prospect.

    `quora_url: str | None`
    :   The prospect’s Quora URL.

    `real_creator_id: int | None`
    :   Real creator ID

    `real_creator_type: str | None`
    :   Real creator type

    `region: str | None`
    :   The primary geographic region of the prospect.

    `reply_count: int | None`
    :   The number of replies the prospect has made since the last touch point.

    `school: str | None`
    :   The school(s) the prospect has attended.

    `score: float | None`
    :   A custom score given to measure the quality of the lead.

    `sharing_team_id: str | None`
    :   The ID of the sharing team associated with this object. Access is currently in beta.

    `sms_opted_out: bool | None`
    :   Sms opted out

    `source: str | None`
    :   A custom source representing where the lead was first acquired.

    `specialties: str | None`
    :   A description of the prospect’s specialties.

    `stack_overflow_id: str | None`
    :   The prospect’s StackOverflow ID.

    `stack_overflow_url: str | None`
    :   The prospect’s StackOverflow URL.

    `stage_name: str | None`
    :   Stage name

    `tags: list[str | None] | None`
    :   The type of the None singleton.

    `time_zone: str | None`
    :   The prospect’s current timezone, preferably in the IANA format (e.g. 'America/LosAngeles').

    `time_zone_iana: str | None`
    :   The prospect’s current IANA timezone, if available.

    `time_zone_inferred: str | None`
    :   The prospect’s current inferred IANA timezone, if available.

    `title: str | None`
    :   The type of the None singleton.

    `touched_at: str | None`
    :   The date and time the prospect was last touched.

    `trashed_at: str | None`
    :   The date a prospect was soft deleted.

    `twitter_url: str | None`
    :   The prospect’s Twitter URL.

    `twitter_username: str | None`
    :   The prospect’s Twitter username.

    `updated_at: str | None`
    :   The type of the None singleton.

    `updater_id: int | None`
    :   Updater ID

    `updater_type: str | None`
    :   Updater type

    `voip_phones: list[str] | None`
    :   A list of voip phone numbers associated with the prospect.

    `website_url1: str | None`
    :   The URL of the prospect’s website.

    `website_url2: str | None`
    :   The value of the prospect’s second website URL field.

    `website_url3: str | None`
    :   The value of the prospect’s third website URL field.

    `work_phones: list[str] | None`
    :   A list of work phone numbers associated with the prospect.

<a id="ProspectLinks"></a>

`ProspectLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="ProspectResponse"></a>

`ProspectResponse(**data: Any)`
:   ProspectResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Prospect | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProspectsList"></a>

`ProspectsList(**data: Any)`
:   ProspectsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Prospect] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProspectsListResultMeta"></a>

`ProspectsListResultMeta(**data: Any)`
:   Metadata for prospects.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="Sequence"></a>

`Sequence(**data: Any)`
:   Outreach sequence object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.SequenceAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.SequenceLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="SequenceAttributes"></a>

`SequenceAttributes(**data: Any)`
:   Nested schema for Sequence.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ai_template_powered: bool | None`
    :   AI template powered

    `automation_percentage: float | None`
    :   The percentage of 'auto_email' sequence steps in this sequence.

    `bounce_count: int | None`
    :   The total count of bounced mailings during this sequence.

    `click_count: int | None`
    :   The total count of clicked mailings from this sequence.

    `created_at: str | None`
    :   The type of the None singleton.

    `deliver_count: int | None`
    :   The total count of delivered mailings from this sequence.

    `description: str | None`
    :   The type of the None singleton.

    `duration_in_days: int | None`
    :   The total number of days it takes to get through this sequence.

    `enabled: bool | None`
    :   The type of the None singleton.

    `enabled_at: str | None`
    :   The date and time the sequence was enabled, or null if currently disabled.

    `failure_count: int | None`
    :   The total count of failed mailings from this sequence.

    `finish_on_reply: bool | None`
    :   Deprecated. This boolean value exists only to maintain backward compatibility and primaryReplyAction should be used instead. True if primaryReplyAction is 'finish', false otherwise.

    `last_used_at: str | None`
    :   The date and time the sequence was last used.

    `locked: bool | None`
    :   A boolean value determining whether the sequence is locked or not.

    `locked_at: str | None`
    :   The date and time the sequence was locked, or null if currently unlocked.

    `max_activations: int | None`
    :   The maximum number of prospects that can be associated with the sequence. Only applies if the sequence type is 'date'.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `negative_reply_count: int | None`
    :   The total count of negative reply mailings from this sequence.

    `neutral_reply_count: int | None`
    :   The total count of neutral reply mailings from this sequence.

    `num_contacted_prospects: int | None`
    :   The total count of prospects who have been either called or emailed.

    `num_replied_prospects: int | None`
    :   The total count of prospects who have been marked as replied.

    `open_count: int | None`
    :   The total count of opened mailings from this sequence.

    `opt_out_count: int | None`
    :   The total count of opted out mailings from this sequence.

    `positive_reply_count: int | None`
    :   The total count of positive reply mailings from this sequence.

    `primary_reply_action: str | None`
    :   The action to take when the primary prospect replies. Must be one of 'finish', 'continue', or 'pause'.

    `primary_reply_pause_duration: int | None`
    :   The duration in seconds to pause for (before automatically finishing) after a reply from the primary prospect if the primaryReplyAction is 'pause'.

    `prospect_click_count: int | None`
    :   Prospect click count

    `prospect_contacted_count: int | None`
    :   Prospect contacted count

    `prospect_deliver_count: int | None`
    :   Prospect deliver count

    `prospect_open_count: int | None`
    :   Prospect open count

    `prospect_reply_count: int | None`
    :   Prospect reply count

    `reply_count: int | None`
    :   The total count of replied mailings from this sequence.

    `sales_motion: str | None`
    :   The sales engagement type of the sequence.

    `schedule_count: int | None`
    :   The total count of scheduled mailings from this sequence.

    `schedule_interval_type: str | None`
    :   The schedule interval type must be either 'calendar' or 'schedule'

    `secondary_reply_action: str | None`
    :   The action to take when someone other than the primary prospect replies. Must be one of 'finish', 'continue', or 'pause'.

    `secondary_reply_pause_duration: int | None`
    :   The duration in seconds to pause for (before automatically finishing) after a reply from anyone other than the primary prospect if the secondaryReplyAction is 'pause'.

    `sequence_step_count: int | None`
    :   The total number of sequence steps in this sequence.

    `sequence_type: str | None`
    :   The type of the None singleton.

    `share_type: str | None`
    :   The sequence share type must be either 'private', 'read_only' or 'shared'.

    `tags: list[str | None] | None`
    :   The type of the None singleton.

    `throttle_capacity: int | None`
    :   The maximum number of associated sequence states per user that can be active at a one time.

    `throttle_max_adds_per_day: int | None`
    :   The maximum number of associated sequence states per user that can be added to the sequence each day.

    `throttle_paused: bool | None`
    :   A boolean value determining whether the throttling of sequence states is paused or not.

    `throttle_paused_at: str | None`
    :   The date and time the sequence state throttling was paused, or null if not currently paused.

    `transactional: bool | None`
    :   A boolean value determining whether prospect opt out preferences are respected. Intended only for non-marketing sequences.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="SequenceLinks"></a>

`SequenceLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="SequenceResponse"></a>

`SequenceResponse(**data: Any)`
:   SequenceResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Sequence | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SequenceState"></a>

`SequenceState(**data: Any)`
:   Outreach sequence state object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.SequenceStateAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="SequenceStateAttributes"></a>

`SequenceStateAttributes(**data: Any)`
:   Nested schema for SequenceState.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `state_changed_at: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="SequenceStateResponse"></a>

`SequenceStateResponse(**data: Any)`
:   SequenceStateResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.SequenceState | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SequenceStatesList"></a>

`SequenceStatesList(**data: Any)`
:   SequenceStatesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.SequenceState] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SequenceStatesListResultMeta"></a>

`SequenceStatesListResultMeta(**data: Any)`
:   Metadata for sequence_states.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="SequenceStep"></a>

`SequenceStep(**data: Any)`
:   Outreach sequence step object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.SequenceStepAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.SequenceStepLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="SequenceStepAttributes"></a>

`SequenceStepAttributes(**data: Any)`
:   Nested schema for SequenceStep.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bounce_count: int | None`
    :   The total count of bounced mailings during this sequence step.

    `call_completed_count: int | None`
    :   Call completed count

    `call_no_answer_count: int | None`
    :   Call no answer count

    `click_count: int | None`
    :   The total count of clicked mailings from this sequence step.

    `created_at: str | None`
    :   The type of the None singleton.

    `date: str | None`
    :   The date this step will activate; only applicable to date-based sequences.

    `deliver_count: int | None`
    :   The total count of delivered mailings from this sequence step.

    `display_name: str | None`
    :   A human-readable display name that captures the step’s type and order.

    `failure_count: int | None`
    :   The total count of failed mailings from this sequence step.

    `interval: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `negative_reply_count: int | None`
    :   The total count of negative reply mailings from this sequence step.

    `neutral_reply_count: int | None`
    :   The total count of neutral reply mailings from this sequence step.

    `open_count: int | None`
    :   The total count of opened mailings from this sequence step.

    `opt_out_count: int | None`
    :   The total count of opted out mailings from this sequence step.

    `order: int | None`
    :   The type of the None singleton.

    `positive_reply_count: int | None`
    :   The total count of positive reply mailings from this sequence step.

    `reply_count: int | None`
    :   The total count of replied mailings from this sequence step.

    `schedule_count: int | None`
    :   The total count of scheduled mailings from this sequence step.

    `step_type: str | None`
    :   The type of the None singleton.

    `task_autoskip_delay: int | None`
    :   The optional interval (in seconds) from when tasks created by this sequence step are overdue until they are automatically skipped.

    `task_note: str | None`
    :   An optional note to associate with created tasks.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="SequenceStepLinks"></a>

`SequenceStepLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="SequenceStepResponse"></a>

`SequenceStepResponse(**data: Any)`
:   SequenceStepResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.SequenceStep | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SequenceStepsList"></a>

`SequenceStepsList(**data: Any)`
:   SequenceStepsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.SequenceStep] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SequenceStepsListResultMeta"></a>

`SequenceStepsListResultMeta(**data: Any)`
:   Metadata for sequence_steps.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="SequencesList"></a>

`SequencesList(**data: Any)`
:   SequencesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Sequence] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SequencesListResultMeta"></a>

`SequencesListResultMeta(**data: Any)`
:   Metadata for sequences.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="Snippet"></a>

`Snippet(**data: Any)`
:   Outreach snippet object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.SnippetAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.SnippetLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="SnippetAttributes"></a>

`SnippetAttributes(**data: Any)`
:   Nested schema for Snippet.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body_html: str | None`
    :   The type of the None singleton.

    `body_text: str | None`
    :   The text of the snippet.

    `contains_custom_html: bool | None`
    :   Contains custom html

    `created_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `share_type: str | None`
    :   The permissions for sharing the snippet; must be 'private' or 'shared.'

    `tags: list[str] | None`
    :   A list of tags associated with the snippet (e.g. ['Useful', 'Prospecting']).

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="SnippetLinks"></a>

`SnippetLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="SnippetResponse"></a>

`SnippetResponse(**data: Any)`
:   SnippetResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Snippet | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SnippetsList"></a>

`SnippetsList(**data: Any)`
:   SnippetsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Snippet] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SnippetsListResultMeta"></a>

`SnippetsListResultMeta(**data: Any)`
:   Metadata for snippets.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="Stage"></a>

`Stage(**data: Any)`
:   Outreach stage object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.StageAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.StageLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="StageAttributes"></a>

`StageAttributes(**data: Any)`
:   Nested schema for Stage.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The color the stage label will be highlighted in the interface, specified as a hexidecimal value (e.g. '#5951ff').

    `created_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `order: int | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="StageLinks"></a>

`StageLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="StageResponse"></a>

`StageResponse(**data: Any)`
:   StageResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Stage | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="StagesList"></a>

`StagesList(**data: Any)`
:   StagesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Stage] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="StagesListResultMeta"></a>

`StagesListResultMeta(**data: Any)`
:   Metadata for stages.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="Task"></a>

`Task(**data: Any)`
:   Outreach task object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.TaskAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.TaskLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="TaskAttributes"></a>

`TaskAttributes(**data: Any)`
:   Nested schema for Task.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action: str | None`
    :   The type of the None singleton.

    `autoskip_at: str | None`
    :   The optional date and time when the task will automatically be skipped. Tasks with an empty autoskip_at will never be autoskipped.

    `compiled_sequence_template_html: str | None`
    :   The compiled template HTML of incomplete SMS or LinkedIn tasks associated with a sequence.

    `completed: bool | None`
    :   A boolean value whether the task has been completed.

    `completed_at: str | None`
    :   The date and time the task was completed.

    `created_at: str | None`
    :   The type of the None singleton.

    `due_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `opportunity_association: str | None`
    :   The optional opportunity rule associated with the task. Can be 'recent_created', 'recent_updated', 'noop'.

    `scheduled_at: str | None`
    :   The date and time the pending task is scheduled for.

    `state: str | None`
    :   The type of the None singleton.

    `state_changed_at: str | None`
    :   The date and time the state last changed.

    `task_type: str | None`
    :   The type of task. Can be 'follow_up', 'manual', 'no_reply', 'sequence_open', 'sequence_click', 'sequence_step_call', 'sequence_step_email', 'sequence_step_linkedin_interact_with_post', 'sequence_step_linkedin_other', 'sequence_step_linkedin_send_connection_request', 'sequence_step_linkedin_send_message', 'sequence_step_linkedin_view_profile', 'sequence_step_sms', 'sequence_step_task', or 'touch'. Tasks created through the API will automatically be 'manual' tasks.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="TaskLinks"></a>

`TaskLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="TaskResponse"></a>

`TaskResponse(**data: Any)`
:   TaskResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Task | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TasksList"></a>

`TasksList(**data: Any)`
:   TasksList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Task] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TasksListResultMeta"></a>

`TasksListResultMeta(**data: Any)`
:   Metadata for tasks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="Template"></a>

`Template(**data: Any)`
:   Outreach template object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.TemplateAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.TemplateLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="TemplateAttributes"></a>

`TemplateAttributes(**data: Any)`
:   Nested schema for Template.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Boolean value indicating if the template has been archived.

    `archived_at: str | None`
    :   The date and time the template was archived.

    `bcc_recipients: list[str] | None`
    :   A list of default person and email address pairs to receive this template in the 'bcc' field (e.g. [Billy Bob `<billy.bob@seattle.city>`])

    `body_html: str | None`
    :   The type of the None singleton.

    `body_text: str | None`
    :   The body text of the template.

    `bounce_count: int | None`
    :   The total count of bounced mailings during this template.

    `cc_recipients: list[str] | None`
    :   A list of default person and email address pairs to receive this template in the 'cc' field (e.g. [Billy Bob `<billy.bob@seattle.city>`])

    `click_count: int | None`
    :   The total count of clicked mailings from this template.

    `contains_custom_html: bool | None`
    :   Contains custom html

    `created_at: str | None`
    :   The type of the None singleton.

    `deliver_count: int | None`
    :   The total count of delivered mailings from this template.

    `failure_count: int | None`
    :   The total count of failed mailings from this template.

    `has_ai_content: bool | None`
    :   Has AI content

    `has_ai_subject_line: bool | None`
    :   Has AI subject line

    `last_used_at: str | None`
    :   The last time the template was used.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `negative_reply_count: int | None`
    :   The total count of negative reply mailings from this template.

    `neutral_reply_count: int | None`
    :   The total count of neutral reply mailings from this template.

    `open_count: int | None`
    :   The total count of opened mailings from this template.

    `opt_out_count: int | None`
    :   The total count of opted out mailings from this template.

    `personalization_ids: list[typing.Any] | None`
    :   Personalization ids

    `positive_reply_count: int | None`
    :   The total count of positive reply mailings from this template.

    `reply_count: int | None`
    :   The total count of replied mailings from this template.

    `schedule_count: int | None`
    :   The total count of scheduled mailings from this template.

    `share_type: str | None`
    :   The share type must be one of 'read_only,' 'private,' or 'shared'.

    `subject: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   A list of tag values associated with the template (e.g. ['Sequencing', 'Quick Response']).

    `to_recipients: list[str] | None`
    :   A list of default person and email address pairs to receive this template in the 'to' field (e.g. ['Billy Bob &lt;billy.bob@seattle.city&gt;'])

    `track_links: bool | None`
    :   Boolean value indicating if link tracking is on for the template.

    `track_opens: bool | None`
    :   Boolean value indicating if open tracking is on for the template.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="TemplateLinks"></a>

`TemplateLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="TemplateResponse"></a>

`TemplateResponse(**data: Any)`
:   TemplateResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.Template | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TemplatesList"></a>

`TemplatesList(**data: Any)`
:   TemplatesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.Template] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TemplatesListResultMeta"></a>

`TemplatesListResultMeta(**data: Any)`
:   Metadata for templates.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

<a id="User"></a>

`User(**data: Any)`
:   Outreach user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.outreach.models.UserAttributes | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.UserLinks | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="UserAttributes"></a>

`UserAttributes(**data: Any)`
:   Nested schema for User.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accounts_view_id: int | None`
    :   The default smart view to load on the account index view.

    `active_prospects_count: int | None`
    :   Active prospects count

    `activity_notifications_disabled: bool | None`
    :   A boolean value whether the user's activity notifications are disabled.

    `bounce_warning_email_enabled: bool | None`
    :   A boolean value whether the user's bounce warning emails are enabled.

    `bridge_phone: str | None`
    :   The telephone number of the user's outbound bridge phone.

    `bridge_phone_extension: str | None`
    :   The extension number of the user's outbound bridge phone.

    `calls_view_id: int | None`
    :   The default smart view to load on the calls view.

    `controlled_tab_default: str | None`
    :   The user's preferred default tab to open when in task flow.

    `created_at: str | None`
    :   The type of the None singleton.

    `current_sign_in_at: str | None`
    :   The date and time the user most recently signed in.

    `custom1: str | None`
    :   The value of the user's first custom field.

    `custom2: str | None`
    :   The value of the user's second custom field.

    `custom3: str | None`
    :   The value of the user's third custom field.

    `custom4: str | None`
    :   The value of the user's fourth custom field.

    `custom5: str | None`
    :   The value of the user's fifth custom field.

    `daily_digest_email_enabled: bool | None`
    :   A boolean value whether the user's daily digest emails are enabled.

    `default_ruleset_id: int | None`
    :   The id of the default ruleset assigned to the user.

    `default_schedule_id: int | None`
    :   Default schedule ID

    `duties: typing.Any | None`
    :   A collection of the user's work roles.

    `duties_set_at: str | None`
    :   Duties set at

    `email: str | None`
    :   The type of the None singleton.

    `enable_voice_recordings: bool | None`
    :   A boolean value whether the user has voice recordings enabled.

    `engagement_emails_enabled: bool | None`
    :   A boolean value whether the user has engagement emails enabled.

    `first_name: str | None`
    :   The type of the None singleton.

    `global_id: str | None`
    :   Global ID

    `guest: bool | None`
    :   Guest

    `inbound_bridge_phone: str | None`
    :   The telephone number of the user's inbound bridge phone.

    `inbound_bridge_phone_extension: str | None`
    :   The extension number of the user's inbound bridge phone.

    `inbound_call_behavior: str | None`
    :   The behavior of inbound calls. Must be either 'inbound_bridge' or 'inbound_voicemail'.

    `inbound_phone_type: str | None`
    :   The user's type of telephone for inbound calls. Must be either 'bridge', 'voip' or 'bridge_and_voip'.

    `inbound_voicemail_custom_message_text: str | None`
    :   The message for inbound voicemails (e.g. 'Please leave a message and I will get back to you as soon I can').

    `inbound_voicemail_message_text_voice: str | None`
    :   The gender of the voice that reads the voicemail message. Must be either 'man' or 'woman'.

    `inbound_voicemail_prompt_type: str | None`
    :   The type of inbound voicemail to use. Must be either 'automated', 'recorded', or 'off'.

    `job_role_by_name: str | None`
    :   The name of the job role (e.g. 'SDR').

    `job_title_extraction_notification_enabled: bool | None`
    :   Job title extraction notification enabled

    `kaia_recordings_view_id: int | None`
    :   The default smart view to load on the kaia recordings view.

    `keep_bridge_phone_connected: bool | None`
    :   Whether to keep the user's bridge phone connected in-between outbound calls.

    `language_preference: str | None`
    :   Language preference

    `last_name: str | None`
    :   The type of the None singleton.

    `last_sign_in_at: str | None`
    :   The date and time the user previously signed in.

    `link_to_sequence_state_in_task_flow: bool | None`
    :   Link to sequence state in task flow

    `locked: bool | None`
    :   A boolean value whether the user is locked out of the application.

    `mailbox_error_email_enabled: bool | None`
    :   A boolean value whether the user's mailbox error emails are enabled.

    `mailings_delivered_count: int | None`
    :   Mailings delivered count

    `mailings_replied_count: int | None`
    :   Mailings replied count

    `meeting_engagement_notification_enabled: bool | None`
    :   A boolean value whether the user's meeting engagement notifications are enabled.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The full name of the user.

    `notifications_enabled: bool | None`
    :   A boolean value whether the user's notifications are enabled.

    `oce_click_to_dial_everywhere: bool | None`
    :   A boolean value indicating if phone calls will launch a call from Outreach (Salesforce, Github, Gmail, LinkedIn, and Twitter).

    `oce_gmail_toolbar: bool | None`
    :   A boolean value indicating whether the Outreach Gmail toolbar is enabled.

    `oce_gmail_tracking_state: str | None`
    :   The user's current email tracking settings when using Outreach Everywhere with GMail.

    `oce_salesforce_email_decorating: bool | None`
    :   A boolean value indicating if emails are enabled in Outreach Everywhere with Salesforce.

    `oce_salesforce_phone_decorating: bool | None`
    :   A boolean value indicating if phone calls are enabled in Outreach Everywhere with Salesforce.

    `oce_universal_task_flow: bool | None`
    :   A boolean value indicating whether Outreach Everywhere universal task flow is enabled.

    `oce_window_mode: bool | None`
    :   A boolean value indicating whether Outreach Everywhere window mode is enabled.

    `onboarded_at: str | None`
    :   Onboarded at

    `opportunities_view_id: int | None`
    :   The default smart view to load on the opportunity index view.

    `orca_standalone_enabled: bool | None`
    :   ORCA standalone enabled

    `password_expires_at: str | None`
    :   The date and time the current password expires.

    `phone_country_code: str | None`
    :   The country code of the user's phone.

    `phone_number: str | None`
    :   The telephone number of the user's phone.

    `phone_type: str | None`
    :   The user's type of telephone for outbound calls. Must be either 'bridge' or 'voip'.

    `plugin_alert_notification_enabled: bool | None`
    :   A boolean value whether the user's plugin related error notifications are enabled.

    `preferred_voice_region: str | None`
    :   A string that represents Twilio data center used to connect to Twilio.

    `prefers_local_presence: bool | None`
    :   A boolean value whether the user prefers that a voice call comes from a local phone number.

    `prospect_detail_default: str | None`
    :   Prospect detail default

    `prospects_view_id: int | None`
    :   The default smart view to load on the prospect index view.

    `reports_team_perf_view_id: int | None`
    :   The default smart view to load on the team performance reports view.

    `reports_view_id: int | None`
    :   The default smart view to load on the reports view.

    `scim_external_id: str | None`
    :   The ID from the SCIM provisioning service used to create the user.

    `scim_source: str | None`
    :   The name of the SCIM provisioning source used to create the user.

    `sender_notifications_excluded: bool | None`
    :   A boolean value whether the user's sender notifications are excluded.

    `tasks_due_count: int | None`
    :   Tasks due count

    `tasks_view_id: int | None`
    :   The default smart view to load on the tasks index view.

    `teams_view_id: int | None`
    :   The default smart view to load on the teams index view.

    `texting_email_notifications: bool | None`
    :   A boolean value whether to send the user email notifications when a text message is missed.

    `title: str | None`
    :   The user's job title (e.g. 'Staff Accountant').

    `unknown_reply_email_enabled: bool | None`
    :   A boolean value whether the user's unknown reply emails are enabled.

    `updated_at: str | None`
    :   The type of the None singleton.

    `use_sales_navigator_for_linked_in_tasks: bool | None`
    :   Use sales navigator for linked in tasks

    `user_guid: str | None`
    :   The globally unique ID (GUID) assigned to the user.

    `username: str | None`
    :   A reader friendly unique identifier of the user.

    `users_view_id: int | None`
    :   The default smart view to load on the users index view.

    `voicemail_notification_enabled: bool | None`
    :   A boolean value whether the user's voicemail notifications are enabled.

    `weekly_digest_email_enabled: bool | None`
    :   A boolean value whether the user's weekly digest email are enabled.

<a id="UserLinks"></a>

`UserLinks(**data: Any)`
:   Links associated with this resource
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | None`
    :   URL for this resource

<a id="UserResponse"></a>

`UserResponse(**data: Any)`
:   UserResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.outreach.models.User | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="UsersList"></a>

`UsersList(**data: Any)`
:   UsersList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.outreach.models.User] | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.outreach.models.PaginationLinks | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="UsersListResultMeta"></a>

`UsersListResultMeta(**data: Any)`
:   Metadata for users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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