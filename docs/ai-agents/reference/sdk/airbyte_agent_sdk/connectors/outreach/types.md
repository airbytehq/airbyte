---
id: airbyte_agent_sdk-connectors-outreach-types
title: airbyte_agent_sdk.connectors.outreach.types
---

Module airbyte_agent_sdk.connectors.outreach.types
==================================================
Type definitions for outreach connector.

Classes
-------

<a id="AccountsAndCondition"></a>

`AccountsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.AccountsEqCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsGtCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsGteCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsLtCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsLteCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsInCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsNotCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsAndCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsOrCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AccountsAnyCondition"></a>

`AccountsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsAnyValueFilter"></a>

`AccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assigned_teams: Any`
    :   Assigned teams

    `assigned_users: Any`
    :   Assigned users

    `batches: Any`
    :   Batches

    `buyer_intent_score: Any`
    :   Buyer intent score

    `company_type: Any`
    :   Company type

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `custom1: Any`
    :   Custom field 1

    `custom10: Any`
    :   Custom field 10

    `custom100: Any`
    :   Custom field 100

    `custom101: Any`
    :   Custom field 101

    `custom102: Any`
    :   Custom field 102

    `custom103: Any`
    :   Custom field 103

    `custom104: Any`
    :   Custom field 104

    `custom105: Any`
    :   Custom field 105

    `custom106: Any`
    :   Custom field 106

    `custom107: Any`
    :   Custom field 107

    `custom108: Any`
    :   Custom field 108

    `custom109: Any`
    :   Custom field 109

    `custom11: Any`
    :   Custom field 11

    `custom110: Any`
    :   Custom field 110

    `custom111: Any`
    :   Custom field 111

    `custom112: Any`
    :   Custom field 112

    `custom113: Any`
    :   Custom field 113

    `custom114: Any`
    :   Custom field 114

    `custom115: Any`
    :   Custom field 115

    `custom116: Any`
    :   Custom field 116

    `custom117: Any`
    :   Custom field 117

    `custom118: Any`
    :   Custom field 118

    `custom119: Any`
    :   Custom field 119

    `custom12: Any`
    :   Custom field 12

    `custom120: Any`
    :   Custom field 120

    `custom121: Any`
    :   Custom field 121

    `custom122: Any`
    :   Custom field 122

    `custom123: Any`
    :   Custom field 123

    `custom124: Any`
    :   Custom field 124

    `custom125: Any`
    :   Custom field 125

    `custom126: Any`
    :   Custom field 126

    `custom127: Any`
    :   Custom field 127

    `custom128: Any`
    :   Custom field 128

    `custom129: Any`
    :   Custom field 129

    `custom13: Any`
    :   Custom field 13

    `custom130: Any`
    :   Custom field 130

    `custom131: Any`
    :   Custom field 131

    `custom132: Any`
    :   Custom field 132

    `custom133: Any`
    :   Custom field 133

    `custom134: Any`
    :   Custom field 134

    `custom135: Any`
    :   Custom field 135

    `custom136: Any`
    :   Custom field 136

    `custom137: Any`
    :   Custom field 137

    `custom138: Any`
    :   Custom field 138

    `custom139: Any`
    :   Custom field 139

    `custom14: Any`
    :   Custom field 14

    `custom140: Any`
    :   Custom field 140

    `custom141: Any`
    :   Custom field 141

    `custom142: Any`
    :   Custom field 142

    `custom143: Any`
    :   Custom field 143

    `custom144: Any`
    :   Custom field 144

    `custom145: Any`
    :   Custom field 145

    `custom146: Any`
    :   Custom field 146

    `custom147: Any`
    :   Custom field 147

    `custom148: Any`
    :   Custom field 148

    `custom149: Any`
    :   Custom field 149

    `custom15: Any`
    :   Custom field 15

    `custom150: Any`
    :   Custom field 150

    `custom16: Any`
    :   Custom field 16

    `custom17: Any`
    :   Custom field 17

    `custom18: Any`
    :   Custom field 18

    `custom19: Any`
    :   Custom field 19

    `custom2: Any`
    :   Custom field 2

    `custom20: Any`
    :   Custom field 20

    `custom21: Any`
    :   Custom field 21

    `custom22: Any`
    :   Custom field 22

    `custom23: Any`
    :   Custom field 23

    `custom24: Any`
    :   Custom field 24

    `custom25: Any`
    :   Custom field 25

    `custom26: Any`
    :   Custom field 26

    `custom27: Any`
    :   Custom field 27

    `custom28: Any`
    :   Custom field 28

    `custom29: Any`
    :   Custom field 29

    `custom3: Any`
    :   Custom field 3

    `custom30: Any`
    :   Custom field 30

    `custom31: Any`
    :   Custom field 31

    `custom32: Any`
    :   Custom field 32

    `custom33: Any`
    :   Custom field 33

    `custom34: Any`
    :   Custom field 34

    `custom35: Any`
    :   Custom field 35

    `custom36: Any`
    :   Custom field 36

    `custom37: Any`
    :   Custom field 37

    `custom38: Any`
    :   Custom field 38

    `custom39: Any`
    :   Custom field 39

    `custom4: Any`
    :   Custom field 4

    `custom40: Any`
    :   Custom field 40

    `custom41: Any`
    :   Custom field 41

    `custom42: Any`
    :   Custom field 42

    `custom43: Any`
    :   Custom field 43

    `custom44: Any`
    :   Custom field 44

    `custom45: Any`
    :   Custom field 45

    `custom46: Any`
    :   Custom field 46

    `custom47: Any`
    :   Custom field 47

    `custom48: Any`
    :   Custom field 48

    `custom49: Any`
    :   Custom field 49

    `custom5: Any`
    :   Custom field 5

    `custom50: Any`
    :   Custom field 50

    `custom51: Any`
    :   Custom field 51

    `custom52: Any`
    :   Custom field 52

    `custom53: Any`
    :   Custom field 53

    `custom54: Any`
    :   Custom field 54

    `custom55: Any`
    :   Custom field 55

    `custom56: Any`
    :   Custom field 56

    `custom57: Any`
    :   Custom field 57

    `custom58: Any`
    :   Custom field 58

    `custom59: Any`
    :   Custom field 59

    `custom6: Any`
    :   Custom field 6

    `custom60: Any`
    :   Custom field 60

    `custom61: Any`
    :   Custom field 61

    `custom62: Any`
    :   Custom field 62

    `custom63: Any`
    :   Custom field 63

    `custom64: Any`
    :   Custom field 64

    `custom65: Any`
    :   Custom field 65

    `custom66: Any`
    :   Custom field 66

    `custom67: Any`
    :   Custom field 67

    `custom68: Any`
    :   Custom field 68

    `custom69: Any`
    :   Custom field 69

    `custom7: Any`
    :   Custom field 7

    `custom70: Any`
    :   Custom field 70

    `custom71: Any`
    :   Custom field 71

    `custom72: Any`
    :   Custom field 72

    `custom73: Any`
    :   Custom field 73

    `custom74: Any`
    :   Custom field 74

    `custom75: Any`
    :   Custom field 75

    `custom76: Any`
    :   Custom field 76

    `custom77: Any`
    :   Custom field 77

    `custom78: Any`
    :   Custom field 78

    `custom79: Any`
    :   Custom field 79

    `custom8: Any`
    :   Custom field 8

    `custom80: Any`
    :   Custom field 80

    `custom81: Any`
    :   Custom field 81

    `custom82: Any`
    :   Custom field 82

    `custom83: Any`
    :   Custom field 83

    `custom84: Any`
    :   Custom field 84

    `custom85: Any`
    :   Custom field 85

    `custom86: Any`
    :   Custom field 86

    `custom87: Any`
    :   Custom field 87

    `custom88: Any`
    :   Custom field 88

    `custom89: Any`
    :   Custom field 89

    `custom9: Any`
    :   Custom field 9

    `custom90: Any`
    :   Custom field 90

    `custom91: Any`
    :   Custom field 91

    `custom92: Any`
    :   Custom field 92

    `custom93: Any`
    :   Custom field 93

    `custom94: Any`
    :   Custom field 94

    `custom95: Any`
    :   Custom field 95

    `custom96: Any`
    :   Custom field 96

    `custom97: Any`
    :   Custom field 97

    `custom98: Any`
    :   Custom field 98

    `custom99: Any`
    :   Custom field 99

    `custom_id: Any`
    :   Custom id

    `default_plugin_mapping: Any`
    :   Default plugin mapping

    `description: Any`
    :   Description

    `domain: Any`
    :   Domain

    `external_source: Any`
    :   External source

    `favorites: Any`
    :   Favorites

    `followers: Any`
    :   Followers

    `founded_at: Any`
    :   Founded at

    `id: Any`
    :   Unique account identifier

    `industry: Any`
    :   Industry

    `linked_in_employees: Any`
    :   Linked in employees

    `linked_in_url: Any`
    :   Linked in url

    `locality: Any`
    :   Locality

    `name: Any`
    :   Name

    `named: Any`
    :   Named

    `natural_name: Any`
    :   Natural name

    `number_of_employees: Any`
    :   Number of employees

    `owner: Any`
    :   Owner

    `prospects: Any`
    :   Prospects

    `sharing_team_id: Any`
    :   Sharing team id

    `tags: Any`
    :   Tags

    `tasks: Any`
    :   Tasks

    `touched_at: Any`
    :   Touched at

    `trashed_at: Any`
    :   Trashed at

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

    `website_url: Any`
    :   Website url

<a id="AccountsArrayContainsCondition"></a>

`AccountsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsContainsCondition"></a>

`AccountsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsEndswithCondition"></a>

`AccountsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsEqCondition"></a>

`AccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsFuzzyCondition"></a>

`AccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsGetParams"></a>

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AccountsGtCondition"></a>

`AccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsGteCondition"></a>

`AccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsInCondition"></a>

`AccountsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.AccountsInFilter`
    :   The type of the None singleton.

<a id="AccountsInFilter"></a>

`AccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assigned_teams: list[list[typing.Any]]`
    :   Assigned teams

    `assigned_users: list[list[typing.Any]]`
    :   Assigned users

    `batches: list[list[typing.Any]]`
    :   Batches

    `buyer_intent_score: list[float]`
    :   Buyer intent score

    `company_type: list[str]`
    :   Company type

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `custom1: list[str]`
    :   Custom field 1

    `custom10: list[str]`
    :   Custom field 10

    `custom100: list[str]`
    :   Custom field 100

    `custom101: list[str]`
    :   Custom field 101

    `custom102: list[str]`
    :   Custom field 102

    `custom103: list[str]`
    :   Custom field 103

    `custom104: list[str]`
    :   Custom field 104

    `custom105: list[str]`
    :   Custom field 105

    `custom106: list[str]`
    :   Custom field 106

    `custom107: list[str]`
    :   Custom field 107

    `custom108: list[str]`
    :   Custom field 108

    `custom109: list[str]`
    :   Custom field 109

    `custom11: list[str]`
    :   Custom field 11

    `custom110: list[str]`
    :   Custom field 110

    `custom111: list[str]`
    :   Custom field 111

    `custom112: list[str]`
    :   Custom field 112

    `custom113: list[str]`
    :   Custom field 113

    `custom114: list[str]`
    :   Custom field 114

    `custom115: list[str]`
    :   Custom field 115

    `custom116: list[str]`
    :   Custom field 116

    `custom117: list[str]`
    :   Custom field 117

    `custom118: list[str]`
    :   Custom field 118

    `custom119: list[str]`
    :   Custom field 119

    `custom12: list[str]`
    :   Custom field 12

    `custom120: list[str]`
    :   Custom field 120

    `custom121: list[str]`
    :   Custom field 121

    `custom122: list[str]`
    :   Custom field 122

    `custom123: list[str]`
    :   Custom field 123

    `custom124: list[str]`
    :   Custom field 124

    `custom125: list[str]`
    :   Custom field 125

    `custom126: list[str]`
    :   Custom field 126

    `custom127: list[str]`
    :   Custom field 127

    `custom128: list[str]`
    :   Custom field 128

    `custom129: list[str]`
    :   Custom field 129

    `custom13: list[str]`
    :   Custom field 13

    `custom130: list[str]`
    :   Custom field 130

    `custom131: list[str]`
    :   Custom field 131

    `custom132: list[str]`
    :   Custom field 132

    `custom133: list[str]`
    :   Custom field 133

    `custom134: list[str]`
    :   Custom field 134

    `custom135: list[str]`
    :   Custom field 135

    `custom136: list[str]`
    :   Custom field 136

    `custom137: list[str]`
    :   Custom field 137

    `custom138: list[str]`
    :   Custom field 138

    `custom139: list[str]`
    :   Custom field 139

    `custom14: list[str]`
    :   Custom field 14

    `custom140: list[str]`
    :   Custom field 140

    `custom141: list[str]`
    :   Custom field 141

    `custom142: list[str]`
    :   Custom field 142

    `custom143: list[str]`
    :   Custom field 143

    `custom144: list[str]`
    :   Custom field 144

    `custom145: list[str]`
    :   Custom field 145

    `custom146: list[str]`
    :   Custom field 146

    `custom147: list[str]`
    :   Custom field 147

    `custom148: list[str]`
    :   Custom field 148

    `custom149: list[str]`
    :   Custom field 149

    `custom15: list[str]`
    :   Custom field 15

    `custom150: list[str]`
    :   Custom field 150

    `custom16: list[str]`
    :   Custom field 16

    `custom17: list[str]`
    :   Custom field 17

    `custom18: list[str]`
    :   Custom field 18

    `custom19: list[str]`
    :   Custom field 19

    `custom2: list[str]`
    :   Custom field 2

    `custom20: list[str]`
    :   Custom field 20

    `custom21: list[str]`
    :   Custom field 21

    `custom22: list[str]`
    :   Custom field 22

    `custom23: list[str]`
    :   Custom field 23

    `custom24: list[str]`
    :   Custom field 24

    `custom25: list[str]`
    :   Custom field 25

    `custom26: list[str]`
    :   Custom field 26

    `custom27: list[str]`
    :   Custom field 27

    `custom28: list[str]`
    :   Custom field 28

    `custom29: list[str]`
    :   Custom field 29

    `custom3: list[str]`
    :   Custom field 3

    `custom30: list[str]`
    :   Custom field 30

    `custom31: list[str]`
    :   Custom field 31

    `custom32: list[str]`
    :   Custom field 32

    `custom33: list[str]`
    :   Custom field 33

    `custom34: list[str]`
    :   Custom field 34

    `custom35: list[str]`
    :   Custom field 35

    `custom36: list[str]`
    :   Custom field 36

    `custom37: list[str]`
    :   Custom field 37

    `custom38: list[str]`
    :   Custom field 38

    `custom39: list[str]`
    :   Custom field 39

    `custom4: list[str]`
    :   Custom field 4

    `custom40: list[str]`
    :   Custom field 40

    `custom41: list[str]`
    :   Custom field 41

    `custom42: list[str]`
    :   Custom field 42

    `custom43: list[str]`
    :   Custom field 43

    `custom44: list[str]`
    :   Custom field 44

    `custom45: list[str]`
    :   Custom field 45

    `custom46: list[str]`
    :   Custom field 46

    `custom47: list[str]`
    :   Custom field 47

    `custom48: list[str]`
    :   Custom field 48

    `custom49: list[str]`
    :   Custom field 49

    `custom5: list[str]`
    :   Custom field 5

    `custom50: list[str]`
    :   Custom field 50

    `custom51: list[str]`
    :   Custom field 51

    `custom52: list[str]`
    :   Custom field 52

    `custom53: list[str]`
    :   Custom field 53

    `custom54: list[str]`
    :   Custom field 54

    `custom55: list[str]`
    :   Custom field 55

    `custom56: list[str]`
    :   Custom field 56

    `custom57: list[str]`
    :   Custom field 57

    `custom58: list[str]`
    :   Custom field 58

    `custom59: list[str]`
    :   Custom field 59

    `custom6: list[str]`
    :   Custom field 6

    `custom60: list[str]`
    :   Custom field 60

    `custom61: list[str]`
    :   Custom field 61

    `custom62: list[str]`
    :   Custom field 62

    `custom63: list[str]`
    :   Custom field 63

    `custom64: list[str]`
    :   Custom field 64

    `custom65: list[str]`
    :   Custom field 65

    `custom66: list[str]`
    :   Custom field 66

    `custom67: list[str]`
    :   Custom field 67

    `custom68: list[str]`
    :   Custom field 68

    `custom69: list[str]`
    :   Custom field 69

    `custom7: list[str]`
    :   Custom field 7

    `custom70: list[str]`
    :   Custom field 70

    `custom71: list[str]`
    :   Custom field 71

    `custom72: list[str]`
    :   Custom field 72

    `custom73: list[str]`
    :   Custom field 73

    `custom74: list[str]`
    :   Custom field 74

    `custom75: list[str]`
    :   Custom field 75

    `custom76: list[str]`
    :   Custom field 76

    `custom77: list[str]`
    :   Custom field 77

    `custom78: list[str]`
    :   Custom field 78

    `custom79: list[str]`
    :   Custom field 79

    `custom8: list[str]`
    :   Custom field 8

    `custom80: list[str]`
    :   Custom field 80

    `custom81: list[str]`
    :   Custom field 81

    `custom82: list[str]`
    :   Custom field 82

    `custom83: list[str]`
    :   Custom field 83

    `custom84: list[str]`
    :   Custom field 84

    `custom85: list[str]`
    :   Custom field 85

    `custom86: list[str]`
    :   Custom field 86

    `custom87: list[str]`
    :   Custom field 87

    `custom88: list[str]`
    :   Custom field 88

    `custom89: list[str]`
    :   Custom field 89

    `custom9: list[str]`
    :   Custom field 9

    `custom90: list[str]`
    :   Custom field 90

    `custom91: list[str]`
    :   Custom field 91

    `custom92: list[str]`
    :   Custom field 92

    `custom93: list[str]`
    :   Custom field 93

    `custom94: list[str]`
    :   Custom field 94

    `custom95: list[str]`
    :   Custom field 95

    `custom96: list[str]`
    :   Custom field 96

    `custom97: list[str]`
    :   Custom field 97

    `custom98: list[str]`
    :   Custom field 98

    `custom99: list[str]`
    :   Custom field 99

    `custom_id: list[str]`
    :   Custom id

    `default_plugin_mapping: list[list[typing.Any]]`
    :   Default plugin mapping

    `description: list[str]`
    :   Description

    `domain: list[str]`
    :   Domain

    `external_source: list[str]`
    :   External source

    `favorites: list[list[typing.Any]]`
    :   Favorites

    `followers: list[int]`
    :   Followers

    `founded_at: list[str]`
    :   Founded at

    `id: list[int]`
    :   Unique account identifier

    `industry: list[str]`
    :   Industry

    `linked_in_employees: list[int]`
    :   Linked in employees

    `linked_in_url: list[str]`
    :   Linked in url

    `locality: list[str]`
    :   Locality

    `name: list[str]`
    :   Name

    `named: list[bool]`
    :   Named

    `natural_name: list[str]`
    :   Natural name

    `number_of_employees: list[int]`
    :   Number of employees

    `owner: list[list[typing.Any]]`
    :   Owner

    `prospects: list[list[typing.Any]]`
    :   Prospects

    `sharing_team_id: list[str]`
    :   Sharing team id

    `tags: list[list[typing.Any]]`
    :   Tags

    `tasks: list[list[typing.Any]]`
    :   Tasks

    `touched_at: list[str]`
    :   Touched at

    `trashed_at: list[str]`
    :   Trashed at

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

    `website_url: list[str]`
    :   Website url

<a id="AccountsKeywordCondition"></a>

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsListParams"></a>

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="AccountsLtCondition"></a>

`AccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsLteCondition"></a>

`AccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsNeqCondition"></a>

`AccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsNotCondition"></a>

`AccountsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.AccountsEqCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsGtCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsGteCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsLtCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsLteCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsInCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsNotCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsAndCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsOrCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsAnyCondition`
    :   The type of the None singleton.

<a id="AccountsOrCondition"></a>

`AccountsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.AccountsEqCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsGtCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsGteCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsLtCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsLteCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsInCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsNotCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsAndCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsOrCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AccountsSearchFilter"></a>

`AccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="AccountsSearchQuery"></a>

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.AccountsEqCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsGtCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsGteCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsLtCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsLteCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsInCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsNotCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsAndCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsOrCondition | airbyte_agent_sdk.connectors.outreach.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.AccountsSortFilter]`
    :   The type of the None singleton.

<a id="AccountsSortFilter"></a>

`AccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assigned_teams: Literal['asc', 'desc']`
    :   Assigned teams

    `assigned_users: Literal['asc', 'desc']`
    :   Assigned users

    `batches: Literal['asc', 'desc']`
    :   Batches

    `buyer_intent_score: Literal['asc', 'desc']`
    :   Buyer intent score

    `company_type: Literal['asc', 'desc']`
    :   Company type

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `custom1: Literal['asc', 'desc']`
    :   Custom field 1

    `custom10: Literal['asc', 'desc']`
    :   Custom field 10

    `custom100: Literal['asc', 'desc']`
    :   Custom field 100

    `custom101: Literal['asc', 'desc']`
    :   Custom field 101

    `custom102: Literal['asc', 'desc']`
    :   Custom field 102

    `custom103: Literal['asc', 'desc']`
    :   Custom field 103

    `custom104: Literal['asc', 'desc']`
    :   Custom field 104

    `custom105: Literal['asc', 'desc']`
    :   Custom field 105

    `custom106: Literal['asc', 'desc']`
    :   Custom field 106

    `custom107: Literal['asc', 'desc']`
    :   Custom field 107

    `custom108: Literal['asc', 'desc']`
    :   Custom field 108

    `custom109: Literal['asc', 'desc']`
    :   Custom field 109

    `custom11: Literal['asc', 'desc']`
    :   Custom field 11

    `custom110: Literal['asc', 'desc']`
    :   Custom field 110

    `custom111: Literal['asc', 'desc']`
    :   Custom field 111

    `custom112: Literal['asc', 'desc']`
    :   Custom field 112

    `custom113: Literal['asc', 'desc']`
    :   Custom field 113

    `custom114: Literal['asc', 'desc']`
    :   Custom field 114

    `custom115: Literal['asc', 'desc']`
    :   Custom field 115

    `custom116: Literal['asc', 'desc']`
    :   Custom field 116

    `custom117: Literal['asc', 'desc']`
    :   Custom field 117

    `custom118: Literal['asc', 'desc']`
    :   Custom field 118

    `custom119: Literal['asc', 'desc']`
    :   Custom field 119

    `custom12: Literal['asc', 'desc']`
    :   Custom field 12

    `custom120: Literal['asc', 'desc']`
    :   Custom field 120

    `custom121: Literal['asc', 'desc']`
    :   Custom field 121

    `custom122: Literal['asc', 'desc']`
    :   Custom field 122

    `custom123: Literal['asc', 'desc']`
    :   Custom field 123

    `custom124: Literal['asc', 'desc']`
    :   Custom field 124

    `custom125: Literal['asc', 'desc']`
    :   Custom field 125

    `custom126: Literal['asc', 'desc']`
    :   Custom field 126

    `custom127: Literal['asc', 'desc']`
    :   Custom field 127

    `custom128: Literal['asc', 'desc']`
    :   Custom field 128

    `custom129: Literal['asc', 'desc']`
    :   Custom field 129

    `custom13: Literal['asc', 'desc']`
    :   Custom field 13

    `custom130: Literal['asc', 'desc']`
    :   Custom field 130

    `custom131: Literal['asc', 'desc']`
    :   Custom field 131

    `custom132: Literal['asc', 'desc']`
    :   Custom field 132

    `custom133: Literal['asc', 'desc']`
    :   Custom field 133

    `custom134: Literal['asc', 'desc']`
    :   Custom field 134

    `custom135: Literal['asc', 'desc']`
    :   Custom field 135

    `custom136: Literal['asc', 'desc']`
    :   Custom field 136

    `custom137: Literal['asc', 'desc']`
    :   Custom field 137

    `custom138: Literal['asc', 'desc']`
    :   Custom field 138

    `custom139: Literal['asc', 'desc']`
    :   Custom field 139

    `custom14: Literal['asc', 'desc']`
    :   Custom field 14

    `custom140: Literal['asc', 'desc']`
    :   Custom field 140

    `custom141: Literal['asc', 'desc']`
    :   Custom field 141

    `custom142: Literal['asc', 'desc']`
    :   Custom field 142

    `custom143: Literal['asc', 'desc']`
    :   Custom field 143

    `custom144: Literal['asc', 'desc']`
    :   Custom field 144

    `custom145: Literal['asc', 'desc']`
    :   Custom field 145

    `custom146: Literal['asc', 'desc']`
    :   Custom field 146

    `custom147: Literal['asc', 'desc']`
    :   Custom field 147

    `custom148: Literal['asc', 'desc']`
    :   Custom field 148

    `custom149: Literal['asc', 'desc']`
    :   Custom field 149

    `custom15: Literal['asc', 'desc']`
    :   Custom field 15

    `custom150: Literal['asc', 'desc']`
    :   Custom field 150

    `custom16: Literal['asc', 'desc']`
    :   Custom field 16

    `custom17: Literal['asc', 'desc']`
    :   Custom field 17

    `custom18: Literal['asc', 'desc']`
    :   Custom field 18

    `custom19: Literal['asc', 'desc']`
    :   Custom field 19

    `custom2: Literal['asc', 'desc']`
    :   Custom field 2

    `custom20: Literal['asc', 'desc']`
    :   Custom field 20

    `custom21: Literal['asc', 'desc']`
    :   Custom field 21

    `custom22: Literal['asc', 'desc']`
    :   Custom field 22

    `custom23: Literal['asc', 'desc']`
    :   Custom field 23

    `custom24: Literal['asc', 'desc']`
    :   Custom field 24

    `custom25: Literal['asc', 'desc']`
    :   Custom field 25

    `custom26: Literal['asc', 'desc']`
    :   Custom field 26

    `custom27: Literal['asc', 'desc']`
    :   Custom field 27

    `custom28: Literal['asc', 'desc']`
    :   Custom field 28

    `custom29: Literal['asc', 'desc']`
    :   Custom field 29

    `custom3: Literal['asc', 'desc']`
    :   Custom field 3

    `custom30: Literal['asc', 'desc']`
    :   Custom field 30

    `custom31: Literal['asc', 'desc']`
    :   Custom field 31

    `custom32: Literal['asc', 'desc']`
    :   Custom field 32

    `custom33: Literal['asc', 'desc']`
    :   Custom field 33

    `custom34: Literal['asc', 'desc']`
    :   Custom field 34

    `custom35: Literal['asc', 'desc']`
    :   Custom field 35

    `custom36: Literal['asc', 'desc']`
    :   Custom field 36

    `custom37: Literal['asc', 'desc']`
    :   Custom field 37

    `custom38: Literal['asc', 'desc']`
    :   Custom field 38

    `custom39: Literal['asc', 'desc']`
    :   Custom field 39

    `custom4: Literal['asc', 'desc']`
    :   Custom field 4

    `custom40: Literal['asc', 'desc']`
    :   Custom field 40

    `custom41: Literal['asc', 'desc']`
    :   Custom field 41

    `custom42: Literal['asc', 'desc']`
    :   Custom field 42

    `custom43: Literal['asc', 'desc']`
    :   Custom field 43

    `custom44: Literal['asc', 'desc']`
    :   Custom field 44

    `custom45: Literal['asc', 'desc']`
    :   Custom field 45

    `custom46: Literal['asc', 'desc']`
    :   Custom field 46

    `custom47: Literal['asc', 'desc']`
    :   Custom field 47

    `custom48: Literal['asc', 'desc']`
    :   Custom field 48

    `custom49: Literal['asc', 'desc']`
    :   Custom field 49

    `custom5: Literal['asc', 'desc']`
    :   Custom field 5

    `custom50: Literal['asc', 'desc']`
    :   Custom field 50

    `custom51: Literal['asc', 'desc']`
    :   Custom field 51

    `custom52: Literal['asc', 'desc']`
    :   Custom field 52

    `custom53: Literal['asc', 'desc']`
    :   Custom field 53

    `custom54: Literal['asc', 'desc']`
    :   Custom field 54

    `custom55: Literal['asc', 'desc']`
    :   Custom field 55

    `custom56: Literal['asc', 'desc']`
    :   Custom field 56

    `custom57: Literal['asc', 'desc']`
    :   Custom field 57

    `custom58: Literal['asc', 'desc']`
    :   Custom field 58

    `custom59: Literal['asc', 'desc']`
    :   Custom field 59

    `custom6: Literal['asc', 'desc']`
    :   Custom field 6

    `custom60: Literal['asc', 'desc']`
    :   Custom field 60

    `custom61: Literal['asc', 'desc']`
    :   Custom field 61

    `custom62: Literal['asc', 'desc']`
    :   Custom field 62

    `custom63: Literal['asc', 'desc']`
    :   Custom field 63

    `custom64: Literal['asc', 'desc']`
    :   Custom field 64

    `custom65: Literal['asc', 'desc']`
    :   Custom field 65

    `custom66: Literal['asc', 'desc']`
    :   Custom field 66

    `custom67: Literal['asc', 'desc']`
    :   Custom field 67

    `custom68: Literal['asc', 'desc']`
    :   Custom field 68

    `custom69: Literal['asc', 'desc']`
    :   Custom field 69

    `custom7: Literal['asc', 'desc']`
    :   Custom field 7

    `custom70: Literal['asc', 'desc']`
    :   Custom field 70

    `custom71: Literal['asc', 'desc']`
    :   Custom field 71

    `custom72: Literal['asc', 'desc']`
    :   Custom field 72

    `custom73: Literal['asc', 'desc']`
    :   Custom field 73

    `custom74: Literal['asc', 'desc']`
    :   Custom field 74

    `custom75: Literal['asc', 'desc']`
    :   Custom field 75

    `custom76: Literal['asc', 'desc']`
    :   Custom field 76

    `custom77: Literal['asc', 'desc']`
    :   Custom field 77

    `custom78: Literal['asc', 'desc']`
    :   Custom field 78

    `custom79: Literal['asc', 'desc']`
    :   Custom field 79

    `custom8: Literal['asc', 'desc']`
    :   Custom field 8

    `custom80: Literal['asc', 'desc']`
    :   Custom field 80

    `custom81: Literal['asc', 'desc']`
    :   Custom field 81

    `custom82: Literal['asc', 'desc']`
    :   Custom field 82

    `custom83: Literal['asc', 'desc']`
    :   Custom field 83

    `custom84: Literal['asc', 'desc']`
    :   Custom field 84

    `custom85: Literal['asc', 'desc']`
    :   Custom field 85

    `custom86: Literal['asc', 'desc']`
    :   Custom field 86

    `custom87: Literal['asc', 'desc']`
    :   Custom field 87

    `custom88: Literal['asc', 'desc']`
    :   Custom field 88

    `custom89: Literal['asc', 'desc']`
    :   Custom field 89

    `custom9: Literal['asc', 'desc']`
    :   Custom field 9

    `custom90: Literal['asc', 'desc']`
    :   Custom field 90

    `custom91: Literal['asc', 'desc']`
    :   Custom field 91

    `custom92: Literal['asc', 'desc']`
    :   Custom field 92

    `custom93: Literal['asc', 'desc']`
    :   Custom field 93

    `custom94: Literal['asc', 'desc']`
    :   Custom field 94

    `custom95: Literal['asc', 'desc']`
    :   Custom field 95

    `custom96: Literal['asc', 'desc']`
    :   Custom field 96

    `custom97: Literal['asc', 'desc']`
    :   Custom field 97

    `custom98: Literal['asc', 'desc']`
    :   Custom field 98

    `custom99: Literal['asc', 'desc']`
    :   Custom field 99

    `custom_id: Literal['asc', 'desc']`
    :   Custom id

    `default_plugin_mapping: Literal['asc', 'desc']`
    :   Default plugin mapping

    `description: Literal['asc', 'desc']`
    :   Description

    `domain: Literal['asc', 'desc']`
    :   Domain

    `external_source: Literal['asc', 'desc']`
    :   External source

    `favorites: Literal['asc', 'desc']`
    :   Favorites

    `followers: Literal['asc', 'desc']`
    :   Followers

    `founded_at: Literal['asc', 'desc']`
    :   Founded at

    `id: Literal['asc', 'desc']`
    :   Unique account identifier

    `industry: Literal['asc', 'desc']`
    :   Industry

    `linked_in_employees: Literal['asc', 'desc']`
    :   Linked in employees

    `linked_in_url: Literal['asc', 'desc']`
    :   Linked in url

    `locality: Literal['asc', 'desc']`
    :   Locality

    `name: Literal['asc', 'desc']`
    :   Name

    `named: Literal['asc', 'desc']`
    :   Named

    `natural_name: Literal['asc', 'desc']`
    :   Natural name

    `number_of_employees: Literal['asc', 'desc']`
    :   Number of employees

    `owner: Literal['asc', 'desc']`
    :   Owner

    `prospects: Literal['asc', 'desc']`
    :   Prospects

    `sharing_team_id: Literal['asc', 'desc']`
    :   Sharing team id

    `tags: Literal['asc', 'desc']`
    :   Tags

    `tasks: Literal['asc', 'desc']`
    :   Tasks

    `touched_at: Literal['asc', 'desc']`
    :   Touched at

    `trashed_at: Literal['asc', 'desc']`
    :   Trashed at

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

    `website_url: Literal['asc', 'desc']`
    :   Website url

<a id="AccountsStartswithCondition"></a>

`AccountsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsStringFilter"></a>

`AccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assigned_teams: str`
    :   Assigned teams

    `assigned_users: str`
    :   Assigned users

    `batches: str`
    :   Batches

    `buyer_intent_score: str`
    :   Buyer intent score

    `company_type: str`
    :   Company type

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `custom1: str`
    :   Custom field 1

    `custom10: str`
    :   Custom field 10

    `custom100: str`
    :   Custom field 100

    `custom101: str`
    :   Custom field 101

    `custom102: str`
    :   Custom field 102

    `custom103: str`
    :   Custom field 103

    `custom104: str`
    :   Custom field 104

    `custom105: str`
    :   Custom field 105

    `custom106: str`
    :   Custom field 106

    `custom107: str`
    :   Custom field 107

    `custom108: str`
    :   Custom field 108

    `custom109: str`
    :   Custom field 109

    `custom11: str`
    :   Custom field 11

    `custom110: str`
    :   Custom field 110

    `custom111: str`
    :   Custom field 111

    `custom112: str`
    :   Custom field 112

    `custom113: str`
    :   Custom field 113

    `custom114: str`
    :   Custom field 114

    `custom115: str`
    :   Custom field 115

    `custom116: str`
    :   Custom field 116

    `custom117: str`
    :   Custom field 117

    `custom118: str`
    :   Custom field 118

    `custom119: str`
    :   Custom field 119

    `custom12: str`
    :   Custom field 12

    `custom120: str`
    :   Custom field 120

    `custom121: str`
    :   Custom field 121

    `custom122: str`
    :   Custom field 122

    `custom123: str`
    :   Custom field 123

    `custom124: str`
    :   Custom field 124

    `custom125: str`
    :   Custom field 125

    `custom126: str`
    :   Custom field 126

    `custom127: str`
    :   Custom field 127

    `custom128: str`
    :   Custom field 128

    `custom129: str`
    :   Custom field 129

    `custom13: str`
    :   Custom field 13

    `custom130: str`
    :   Custom field 130

    `custom131: str`
    :   Custom field 131

    `custom132: str`
    :   Custom field 132

    `custom133: str`
    :   Custom field 133

    `custom134: str`
    :   Custom field 134

    `custom135: str`
    :   Custom field 135

    `custom136: str`
    :   Custom field 136

    `custom137: str`
    :   Custom field 137

    `custom138: str`
    :   Custom field 138

    `custom139: str`
    :   Custom field 139

    `custom14: str`
    :   Custom field 14

    `custom140: str`
    :   Custom field 140

    `custom141: str`
    :   Custom field 141

    `custom142: str`
    :   Custom field 142

    `custom143: str`
    :   Custom field 143

    `custom144: str`
    :   Custom field 144

    `custom145: str`
    :   Custom field 145

    `custom146: str`
    :   Custom field 146

    `custom147: str`
    :   Custom field 147

    `custom148: str`
    :   Custom field 148

    `custom149: str`
    :   Custom field 149

    `custom15: str`
    :   Custom field 15

    `custom150: str`
    :   Custom field 150

    `custom16: str`
    :   Custom field 16

    `custom17: str`
    :   Custom field 17

    `custom18: str`
    :   Custom field 18

    `custom19: str`
    :   Custom field 19

    `custom2: str`
    :   Custom field 2

    `custom20: str`
    :   Custom field 20

    `custom21: str`
    :   Custom field 21

    `custom22: str`
    :   Custom field 22

    `custom23: str`
    :   Custom field 23

    `custom24: str`
    :   Custom field 24

    `custom25: str`
    :   Custom field 25

    `custom26: str`
    :   Custom field 26

    `custom27: str`
    :   Custom field 27

    `custom28: str`
    :   Custom field 28

    `custom29: str`
    :   Custom field 29

    `custom3: str`
    :   Custom field 3

    `custom30: str`
    :   Custom field 30

    `custom31: str`
    :   Custom field 31

    `custom32: str`
    :   Custom field 32

    `custom33: str`
    :   Custom field 33

    `custom34: str`
    :   Custom field 34

    `custom35: str`
    :   Custom field 35

    `custom36: str`
    :   Custom field 36

    `custom37: str`
    :   Custom field 37

    `custom38: str`
    :   Custom field 38

    `custom39: str`
    :   Custom field 39

    `custom4: str`
    :   Custom field 4

    `custom40: str`
    :   Custom field 40

    `custom41: str`
    :   Custom field 41

    `custom42: str`
    :   Custom field 42

    `custom43: str`
    :   Custom field 43

    `custom44: str`
    :   Custom field 44

    `custom45: str`
    :   Custom field 45

    `custom46: str`
    :   Custom field 46

    `custom47: str`
    :   Custom field 47

    `custom48: str`
    :   Custom field 48

    `custom49: str`
    :   Custom field 49

    `custom5: str`
    :   Custom field 5

    `custom50: str`
    :   Custom field 50

    `custom51: str`
    :   Custom field 51

    `custom52: str`
    :   Custom field 52

    `custom53: str`
    :   Custom field 53

    `custom54: str`
    :   Custom field 54

    `custom55: str`
    :   Custom field 55

    `custom56: str`
    :   Custom field 56

    `custom57: str`
    :   Custom field 57

    `custom58: str`
    :   Custom field 58

    `custom59: str`
    :   Custom field 59

    `custom6: str`
    :   Custom field 6

    `custom60: str`
    :   Custom field 60

    `custom61: str`
    :   Custom field 61

    `custom62: str`
    :   Custom field 62

    `custom63: str`
    :   Custom field 63

    `custom64: str`
    :   Custom field 64

    `custom65: str`
    :   Custom field 65

    `custom66: str`
    :   Custom field 66

    `custom67: str`
    :   Custom field 67

    `custom68: str`
    :   Custom field 68

    `custom69: str`
    :   Custom field 69

    `custom7: str`
    :   Custom field 7

    `custom70: str`
    :   Custom field 70

    `custom71: str`
    :   Custom field 71

    `custom72: str`
    :   Custom field 72

    `custom73: str`
    :   Custom field 73

    `custom74: str`
    :   Custom field 74

    `custom75: str`
    :   Custom field 75

    `custom76: str`
    :   Custom field 76

    `custom77: str`
    :   Custom field 77

    `custom78: str`
    :   Custom field 78

    `custom79: str`
    :   Custom field 79

    `custom8: str`
    :   Custom field 8

    `custom80: str`
    :   Custom field 80

    `custom81: str`
    :   Custom field 81

    `custom82: str`
    :   Custom field 82

    `custom83: str`
    :   Custom field 83

    `custom84: str`
    :   Custom field 84

    `custom85: str`
    :   Custom field 85

    `custom86: str`
    :   Custom field 86

    `custom87: str`
    :   Custom field 87

    `custom88: str`
    :   Custom field 88

    `custom89: str`
    :   Custom field 89

    `custom9: str`
    :   Custom field 9

    `custom90: str`
    :   Custom field 90

    `custom91: str`
    :   Custom field 91

    `custom92: str`
    :   Custom field 92

    `custom93: str`
    :   Custom field 93

    `custom94: str`
    :   Custom field 94

    `custom95: str`
    :   Custom field 95

    `custom96: str`
    :   Custom field 96

    `custom97: str`
    :   Custom field 97

    `custom98: str`
    :   Custom field 98

    `custom99: str`
    :   Custom field 99

    `custom_id: str`
    :   Custom id

    `default_plugin_mapping: str`
    :   Default plugin mapping

    `description: str`
    :   Description

    `domain: str`
    :   Domain

    `external_source: str`
    :   External source

    `favorites: str`
    :   Favorites

    `followers: str`
    :   Followers

    `founded_at: str`
    :   Founded at

    `id: str`
    :   Unique account identifier

    `industry: str`
    :   Industry

    `linked_in_employees: str`
    :   Linked in employees

    `linked_in_url: str`
    :   Linked in url

    `locality: str`
    :   Locality

    `name: str`
    :   Name

    `named: str`
    :   Named

    `natural_name: str`
    :   Natural name

    `number_of_employees: str`
    :   Number of employees

    `owner: str`
    :   Owner

    `prospects: str`
    :   Prospects

    `sharing_team_id: str`
    :   Sharing team id

    `tags: str`
    :   Tags

    `tasks: str`
    :   Tasks

    `touched_at: str`
    :   Touched at

    `trashed_at: str`
    :   Trashed at

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

    `website_url: str`
    :   Website url

<a id="AirbyteSearchParams"></a>

`AirbyteSearchParams(*args, **kwargs)`
:   Parameters for Airbyte cache search operations (generic, use entity-specific query types for better type hints).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `fields: list[list[str]]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="CallDispositionsAndCondition"></a>

`CallDispositionsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.CallDispositionsEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsInCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAnyCondition]`
    :   The type of the None singleton.

<a id="CallDispositionsAnyCondition"></a>

`CallDispositionsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallDispositionsAnyValueFilter"></a>

`CallDispositionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calls: Any`
    :   Calls

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `default_for_outbound_voicemail: Any`
    :   Default for outbound voicemail

    `id: Any`
    :   Unique call disposition identifier

    `name: Any`
    :   Name

    `order: Any`
    :   Order

    `outcome: Any`
    :   Outcome

    `updated_at: Any`
    :   Updated at

<a id="CallDispositionsArrayContainsCondition"></a>

`CallDispositionsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallDispositionsContainsCondition"></a>

`CallDispositionsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallDispositionsEndswithCondition"></a>

`CallDispositionsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsStringFilter`
    :   The type of the None singleton.

<a id="CallDispositionsEqCondition"></a>

`CallDispositionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsSearchFilter`
    :   The type of the None singleton.

<a id="CallDispositionsFuzzyCondition"></a>

`CallDispositionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsStringFilter`
    :   The type of the None singleton.

<a id="CallDispositionsGetParams"></a>

`CallDispositionsGetParams(*args, **kwargs)`
:   Parameters for call_dispositions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CallDispositionsGtCondition"></a>

`CallDispositionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsSearchFilter`
    :   The type of the None singleton.

<a id="CallDispositionsGteCondition"></a>

`CallDispositionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsSearchFilter`
    :   The type of the None singleton.

<a id="CallDispositionsInCondition"></a>

`CallDispositionsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsInFilter`
    :   The type of the None singleton.

<a id="CallDispositionsInFilter"></a>

`CallDispositionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calls: list[list[typing.Any]]`
    :   Calls

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `default_for_outbound_voicemail: list[bool]`
    :   Default for outbound voicemail

    `id: list[int]`
    :   Unique call disposition identifier

    `name: list[str]`
    :   Name

    `order: list[int]`
    :   Order

    `outcome: list[str]`
    :   Outcome

    `updated_at: list[str]`
    :   Updated at

<a id="CallDispositionsKeywordCondition"></a>

`CallDispositionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsStringFilter`
    :   The type of the None singleton.

<a id="CallDispositionsListParams"></a>

`CallDispositionsListParams(*args, **kwargs)`
:   Parameters for call_dispositions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="CallDispositionsLtCondition"></a>

`CallDispositionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsSearchFilter`
    :   The type of the None singleton.

<a id="CallDispositionsLteCondition"></a>

`CallDispositionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsSearchFilter`
    :   The type of the None singleton.

<a id="CallDispositionsNeqCondition"></a>

`CallDispositionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsSearchFilter`
    :   The type of the None singleton.

<a id="CallDispositionsNotCondition"></a>

`CallDispositionsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsInCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAnyCondition`
    :   The type of the None singleton.

<a id="CallDispositionsOrCondition"></a>

`CallDispositionsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.CallDispositionsEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsInCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAnyCondition]`
    :   The type of the None singleton.

<a id="CallDispositionsSearchFilter"></a>

`CallDispositionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering call_dispositions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `name: str | None`
    :   Name

    `order: int | None`
    :   Order

    `outcome: str | None`
    :   Outcome

    `updated_at: str | None`
    :   Updated at

<a id="CallDispositionsSearchQuery"></a>

`CallDispositionsSearchQuery(*args, **kwargs)`
:   Search query for call_dispositions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsInCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallDispositionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.CallDispositionsSortFilter]`
    :   The type of the None singleton.

<a id="CallDispositionsSortFilter"></a>

`CallDispositionsSortFilter(*args, **kwargs)`
:   Available fields for sorting call_dispositions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calls: Literal['asc', 'desc']`
    :   Calls

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `default_for_outbound_voicemail: Literal['asc', 'desc']`
    :   Default for outbound voicemail

    `id: Literal['asc', 'desc']`
    :   Unique call disposition identifier

    `name: Literal['asc', 'desc']`
    :   Name

    `order: Literal['asc', 'desc']`
    :   Order

    `outcome: Literal['asc', 'desc']`
    :   Outcome

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

<a id="CallDispositionsStartswithCondition"></a>

`CallDispositionsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.CallDispositionsStringFilter`
    :   The type of the None singleton.

<a id="CallDispositionsStringFilter"></a>

`CallDispositionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calls: str`
    :   Calls

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `default_for_outbound_voicemail: str`
    :   Default for outbound voicemail

    `id: str`
    :   Unique call disposition identifier

    `name: str`
    :   Name

    `order: str`
    :   Order

    `outcome: str`
    :   Outcome

    `updated_at: str`
    :   Updated at

<a id="CallPurposesAndCondition"></a>

`CallPurposesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.CallPurposesEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesInCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesAnyCondition]`
    :   The type of the None singleton.

<a id="CallPurposesAnyCondition"></a>

`CallPurposesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.CallPurposesAnyValueFilter`
    :   The type of the None singleton.

<a id="CallPurposesAnyValueFilter"></a>

`CallPurposesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calls: Any`
    :   Calls

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `id: Any`
    :   Unique call purpose identifier

    `name: Any`
    :   Name

    `order: Any`
    :   Order

    `updated_at: Any`
    :   Updated at

<a id="CallPurposesArrayContainsCondition"></a>

`CallPurposesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.CallPurposesAnyValueFilter`
    :   The type of the None singleton.

<a id="CallPurposesContainsCondition"></a>

`CallPurposesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.CallPurposesAnyValueFilter`
    :   The type of the None singleton.

<a id="CallPurposesEndswithCondition"></a>

`CallPurposesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.CallPurposesStringFilter`
    :   The type of the None singleton.

<a id="CallPurposesEqCondition"></a>

`CallPurposesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.CallPurposesSearchFilter`
    :   The type of the None singleton.

<a id="CallPurposesFuzzyCondition"></a>

`CallPurposesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.CallPurposesStringFilter`
    :   The type of the None singleton.

<a id="CallPurposesGetParams"></a>

`CallPurposesGetParams(*args, **kwargs)`
:   Parameters for call_purposes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CallPurposesGtCondition"></a>

`CallPurposesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.CallPurposesSearchFilter`
    :   The type of the None singleton.

<a id="CallPurposesGteCondition"></a>

`CallPurposesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.CallPurposesSearchFilter`
    :   The type of the None singleton.

<a id="CallPurposesInCondition"></a>

`CallPurposesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.CallPurposesInFilter`
    :   The type of the None singleton.

<a id="CallPurposesInFilter"></a>

`CallPurposesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calls: list[list[typing.Any]]`
    :   Calls

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `id: list[int]`
    :   Unique call purpose identifier

    `name: list[str]`
    :   Name

    `order: list[int]`
    :   Order

    `updated_at: list[str]`
    :   Updated at

<a id="CallPurposesKeywordCondition"></a>

`CallPurposesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.CallPurposesStringFilter`
    :   The type of the None singleton.

<a id="CallPurposesListParams"></a>

`CallPurposesListParams(*args, **kwargs)`
:   Parameters for call_purposes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="CallPurposesLtCondition"></a>

`CallPurposesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.CallPurposesSearchFilter`
    :   The type of the None singleton.

<a id="CallPurposesLteCondition"></a>

`CallPurposesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.CallPurposesSearchFilter`
    :   The type of the None singleton.

<a id="CallPurposesNeqCondition"></a>

`CallPurposesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.CallPurposesSearchFilter`
    :   The type of the None singleton.

<a id="CallPurposesNotCondition"></a>

`CallPurposesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.CallPurposesEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesInCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesAnyCondition`
    :   The type of the None singleton.

<a id="CallPurposesOrCondition"></a>

`CallPurposesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.CallPurposesEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesInCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesAnyCondition]`
    :   The type of the None singleton.

<a id="CallPurposesSearchFilter"></a>

`CallPurposesSearchFilter(*args, **kwargs)`
:   Available fields for filtering call_purposes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calls: list[typing.Any] | None`
    :   Calls

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `id: int | None`
    :   Unique call purpose identifier

    `name: str | None`
    :   Name

    `order: int | None`
    :   Order

    `updated_at: str | None`
    :   Updated at

<a id="CallPurposesSearchQuery"></a>

`CallPurposesSearchQuery(*args, **kwargs)`
:   Search query for call_purposes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.CallPurposesEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesInCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallPurposesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.CallPurposesSortFilter]`
    :   The type of the None singleton.

<a id="CallPurposesSortFilter"></a>

`CallPurposesSortFilter(*args, **kwargs)`
:   Available fields for sorting call_purposes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calls: Literal['asc', 'desc']`
    :   Calls

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `id: Literal['asc', 'desc']`
    :   Unique call purpose identifier

    `name: Literal['asc', 'desc']`
    :   Name

    `order: Literal['asc', 'desc']`
    :   Order

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

<a id="CallPurposesStartswithCondition"></a>

`CallPurposesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.CallPurposesStringFilter`
    :   The type of the None singleton.

<a id="CallPurposesStringFilter"></a>

`CallPurposesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calls: str`
    :   Calls

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `id: str`
    :   Unique call purpose identifier

    `name: str`
    :   Name

    `order: str`
    :   Order

    `updated_at: str`
    :   Updated at

<a id="CallsAndCondition"></a>

`CallsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.CallsEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallsGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallsGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallsLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallsLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallsInCondition | airbyte_agent_sdk.connectors.outreach.types.CallsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallsNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallsAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallsOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallsAnyCondition]`
    :   The type of the None singleton.

<a id="CallsAnyCondition"></a>

`CallsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.CallsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallsAnyValueFilter"></a>

`CallsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answered_at: Any`
    :   Answered at

    `batches: Any`
    :   Batches

    `call_disposition: Any`
    :   Call disposition

    `call_purpose: Any`
    :   Call purpose

    `completed_at: Any`
    :   Completed at

    `created_at: Any`
    :   Created at

    `dialed_at: Any`
    :   Dialed at

    `direction: Any`
    :   Direction

    `external_vendor: Any`
    :   External vendor

    `from_: Any`
    :   From

    `id: Any`
    :   Unique call identifier

    `note: Any`
    :   Note

    `opportunity: Any`
    :   Opportunity

    `outbound_voicemail: Any`
    :   Outbound voicemail

    `outcome: Any`
    :   Outcome

    `phone: Any`
    :   Phone

    `phone_number: Any`
    :   Phone number

    `prospect: Any`
    :   Prospect

    `recording_deletion_reason: Any`
    :   Recording deletion reason

    `recording_url: Any`
    :   Recording url

    `returned_at: Any`
    :   Returned at

    `sequence: Any`
    :   Sequence

    `sequence_action: Any`
    :   Sequence action

    `sequence_state: Any`
    :   Sequence state

    `sequence_step: Any`
    :   Sequence step

    `should_record_call: Any`
    :   Should record call

    `state: Any`
    :   State

    `state_changed_at: Any`
    :   State changed at

    `tags: Any`
    :   Tags

    `task: Any`
    :   Task

    `to: Any`
    :   To

    `uid: Any`
    :   Uid

    `updated_at: Any`
    :   Updated at

    `user: Any`
    :   User

    `user_call_type: Any`
    :   User call type

    `vendor_call_id: Any`
    :   Vendor call id

    `voicemail_recording_url: Any`
    :   Voicemail recording url

<a id="CallsArrayContainsCondition"></a>

`CallsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.CallsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallsContainsCondition"></a>

`CallsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.CallsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallsEndswithCondition"></a>

`CallsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsEqCondition"></a>

`CallsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsFuzzyCondition"></a>

`CallsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsGetParams"></a>

`CallsGetParams(*args, **kwargs)`
:   Parameters for calls.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CallsGtCondition"></a>

`CallsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsGteCondition"></a>

`CallsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsInCondition"></a>

`CallsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.CallsInFilter`
    :   The type of the None singleton.

<a id="CallsInFilter"></a>

`CallsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answered_at: list[str]`
    :   Answered at

    `batches: list[list[typing.Any]]`
    :   Batches

    `call_disposition: list[list[typing.Any]]`
    :   Call disposition

    `call_purpose: list[list[typing.Any]]`
    :   Call purpose

    `completed_at: list[str]`
    :   Completed at

    `created_at: list[str]`
    :   Created at

    `dialed_at: list[str]`
    :   Dialed at

    `direction: list[str]`
    :   Direction

    `external_vendor: list[str]`
    :   External vendor

    `from_: list[str]`
    :   From

    `id: list[int]`
    :   Unique call identifier

    `note: list[str]`
    :   Note

    `opportunity: list[list[typing.Any]]`
    :   Opportunity

    `outbound_voicemail: list[list[typing.Any]]`
    :   Outbound voicemail

    `outcome: list[str]`
    :   Outcome

    `phone: list[list[typing.Any]]`
    :   Phone

    `phone_number: list[list[typing.Any]]`
    :   Phone number

    `prospect: list[list[typing.Any]]`
    :   Prospect

    `recording_deletion_reason: list[str]`
    :   Recording deletion reason

    `recording_url: list[str]`
    :   Recording url

    `returned_at: list[str]`
    :   Returned at

    `sequence: list[list[typing.Any]]`
    :   Sequence

    `sequence_action: list[str]`
    :   Sequence action

    `sequence_state: list[list[typing.Any]]`
    :   Sequence state

    `sequence_step: list[list[typing.Any]]`
    :   Sequence step

    `should_record_call: list[bool]`
    :   Should record call

    `state: list[str]`
    :   State

    `state_changed_at: list[str]`
    :   State changed at

    `tags: list[list[typing.Any]]`
    :   Tags

    `task: list[list[typing.Any]]`
    :   Task

    `to: list[str]`
    :   To

    `uid: list[str]`
    :   Uid

    `updated_at: list[str]`
    :   Updated at

    `user: list[list[typing.Any]]`
    :   User

    `user_call_type: list[str]`
    :   User call type

    `vendor_call_id: list[str]`
    :   Vendor call id

    `voicemail_recording_url: list[str]`
    :   Voicemail recording url

<a id="CallsKeywordCondition"></a>

`CallsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsListParams"></a>

`CallsListParams(*args, **kwargs)`
:   Parameters for calls.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="CallsLtCondition"></a>

`CallsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsLteCondition"></a>

`CallsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsNeqCondition"></a>

`CallsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsNotCondition"></a>

`CallsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.CallsEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallsGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallsGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallsLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallsLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallsInCondition | airbyte_agent_sdk.connectors.outreach.types.CallsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallsNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallsAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallsOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallsAnyCondition`
    :   The type of the None singleton.

<a id="CallsOrCondition"></a>

`CallsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.CallsEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallsGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallsGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallsLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallsLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallsInCondition | airbyte_agent_sdk.connectors.outreach.types.CallsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallsNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallsAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallsOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallsAnyCondition]`
    :   The type of the None singleton.

<a id="CallsSearchFilter"></a>

`CallsSearchFilter(*args, **kwargs)`
:   Available fields for filtering calls search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CallsSearchQuery"></a>

`CallsSearchQuery(*args, **kwargs)`
:   Search query for calls entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.CallsEqCondition | airbyte_agent_sdk.connectors.outreach.types.CallsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.CallsGtCondition | airbyte_agent_sdk.connectors.outreach.types.CallsGteCondition | airbyte_agent_sdk.connectors.outreach.types.CallsLtCondition | airbyte_agent_sdk.connectors.outreach.types.CallsLteCondition | airbyte_agent_sdk.connectors.outreach.types.CallsInCondition | airbyte_agent_sdk.connectors.outreach.types.CallsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.CallsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.CallsNotCondition | airbyte_agent_sdk.connectors.outreach.types.CallsAndCondition | airbyte_agent_sdk.connectors.outreach.types.CallsOrCondition | airbyte_agent_sdk.connectors.outreach.types.CallsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.CallsSortFilter]`
    :   The type of the None singleton.

<a id="CallsSortFilter"></a>

`CallsSortFilter(*args, **kwargs)`
:   Available fields for sorting calls search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answered_at: Literal['asc', 'desc']`
    :   Answered at

    `batches: Literal['asc', 'desc']`
    :   Batches

    `call_disposition: Literal['asc', 'desc']`
    :   Call disposition

    `call_purpose: Literal['asc', 'desc']`
    :   Call purpose

    `completed_at: Literal['asc', 'desc']`
    :   Completed at

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `dialed_at: Literal['asc', 'desc']`
    :   Dialed at

    `direction: Literal['asc', 'desc']`
    :   Direction

    `external_vendor: Literal['asc', 'desc']`
    :   External vendor

    `from_: Literal['asc', 'desc']`
    :   From

    `id: Literal['asc', 'desc']`
    :   Unique call identifier

    `note: Literal['asc', 'desc']`
    :   Note

    `opportunity: Literal['asc', 'desc']`
    :   Opportunity

    `outbound_voicemail: Literal['asc', 'desc']`
    :   Outbound voicemail

    `outcome: Literal['asc', 'desc']`
    :   Outcome

    `phone: Literal['asc', 'desc']`
    :   Phone

    `phone_number: Literal['asc', 'desc']`
    :   Phone number

    `prospect: Literal['asc', 'desc']`
    :   Prospect

    `recording_deletion_reason: Literal['asc', 'desc']`
    :   Recording deletion reason

    `recording_url: Literal['asc', 'desc']`
    :   Recording url

    `returned_at: Literal['asc', 'desc']`
    :   Returned at

    `sequence: Literal['asc', 'desc']`
    :   Sequence

    `sequence_action: Literal['asc', 'desc']`
    :   Sequence action

    `sequence_state: Literal['asc', 'desc']`
    :   Sequence state

    `sequence_step: Literal['asc', 'desc']`
    :   Sequence step

    `should_record_call: Literal['asc', 'desc']`
    :   Should record call

    `state: Literal['asc', 'desc']`
    :   State

    `state_changed_at: Literal['asc', 'desc']`
    :   State changed at

    `tags: Literal['asc', 'desc']`
    :   Tags

    `task: Literal['asc', 'desc']`
    :   Task

    `to: Literal['asc', 'desc']`
    :   To

    `uid: Literal['asc', 'desc']`
    :   Uid

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `user: Literal['asc', 'desc']`
    :   User

    `user_call_type: Literal['asc', 'desc']`
    :   User call type

    `vendor_call_id: Literal['asc', 'desc']`
    :   Vendor call id

    `voicemail_recording_url: Literal['asc', 'desc']`
    :   Voicemail recording url

<a id="CallsStartswithCondition"></a>

`CallsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsStringFilter"></a>

`CallsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answered_at: str`
    :   Answered at

    `batches: str`
    :   Batches

    `call_disposition: str`
    :   Call disposition

    `call_purpose: str`
    :   Call purpose

    `completed_at: str`
    :   Completed at

    `created_at: str`
    :   Created at

    `dialed_at: str`
    :   Dialed at

    `direction: str`
    :   Direction

    `external_vendor: str`
    :   External vendor

    `from_: str`
    :   From

    `id: str`
    :   Unique call identifier

    `note: str`
    :   Note

    `opportunity: str`
    :   Opportunity

    `outbound_voicemail: str`
    :   Outbound voicemail

    `outcome: str`
    :   Outcome

    `phone: str`
    :   Phone

    `phone_number: str`
    :   Phone number

    `prospect: str`
    :   Prospect

    `recording_deletion_reason: str`
    :   Recording deletion reason

    `recording_url: str`
    :   Recording url

    `returned_at: str`
    :   Returned at

    `sequence: str`
    :   Sequence

    `sequence_action: str`
    :   Sequence action

    `sequence_state: str`
    :   Sequence state

    `sequence_step: str`
    :   Sequence step

    `should_record_call: str`
    :   Should record call

    `state: str`
    :   State

    `state_changed_at: str`
    :   State changed at

    `tags: str`
    :   Tags

    `task: str`
    :   Task

    `to: str`
    :   To

    `uid: str`
    :   Uid

    `updated_at: str`
    :   Updated at

    `user: str`
    :   User

    `user_call_type: str`
    :   User call type

    `vendor_call_id: str`
    :   Vendor call id

    `voicemail_recording_url: str`
    :   Voicemail recording url

<a id="MailboxesAndCondition"></a>

`MailboxesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.MailboxesEqCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesGtCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesGteCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesLtCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesLteCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesInCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesNotCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesAndCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesOrCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesAnyCondition]`
    :   The type of the None singleton.

<a id="MailboxesAnyCondition"></a>

`MailboxesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.MailboxesAnyValueFilter`
    :   The type of the None singleton.

<a id="MailboxesAnyValueFilter"></a>

`MailboxesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auth_id: Any`
    :   Auth id

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `editable: Any`
    :   Editable

    `email: Any`
    :   Email

    `email_hash: Any`
    :   Email hash

    `email_provider: Any`
    :   Email provider

    `email_signature: Any`
    :   Email signature

    `ews_custom_search_folder: Any`
    :   Ews custom search folder

    `ews_delegate_sync: Any`
    :   Ews delegate sync

    `ews_endpoint: Any`
    :   Ews endpoint

    `ews_impersonation: Any`
    :   Ews impersonation

    `ews_ssl_verify_mode: Any`
    :   Ews ssl verify mode

    `exchange_version: Any`
    :   Exchange version

    `id: Any`
    :   Unique mailbox identifier

    `imap_host: Any`
    :   Imap host

    `imap_port: Any`
    :   Imap port

    `imap_ssl: Any`
    :   Imap ssl

    `mail_aliases: Any`
    :   Mail aliases

    `mailings: Any`
    :   Mailings

    `max_emails_per_day: Any`
    :   Max emails per day

    `max_mailings_per_day: Any`
    :   Max mailings per day

    `max_mailings_per_week: Any`
    :   Max mailings per week

    `opt_out_message: Any`
    :   Opt out message

    `opt_out_signature: Any`
    :   Opt out signature

    `prospect_email_exclusions: Any`
    :   Prospect email exclusions

    `provider_id: Any`
    :   Provider id

    `provider_type: Any`
    :   Provider type

    `send_disabled: Any`
    :   Send disabled

    `send_errored_at: Any`
    :   Send errored at

    `send_max_retries: Any`
    :   Send max retries

    `send_method: Any`
    :   Send method

    `send_period: Any`
    :   Send period

    `send_permanent_error_at: Any`
    :   Send permanent error at

    `send_requires_sync: Any`
    :   Send requires sync

    `send_success_at: Any`
    :   Send success at

    `send_threshold: Any`
    :   Send threshold

    `sendgrid_webhook_url: Any`
    :   Sendgrid webhook url

    `smtp_host: Any`
    :   Smtp host

    `smtp_port: Any`
    :   Smtp port

    `smtp_ssl: Any`
    :   Smtp ssl

    `smtp_username: Any`
    :   Smtp username

    `sync_active_frequency: Any`
    :   Sync active frequency

    `sync_disabled: Any`
    :   Sync disabled

    `sync_errored_at: Any`
    :   Sync errored at

    `sync_finished_at: Any`
    :   Sync finished at

    `sync_method: Any`
    :   Sync method

    `sync_outreach_folder: Any`
    :   Sync outreach folder

    `sync_passive_frequency: Any`
    :   Sync passive frequency

    `sync_permanent_error_at: Any`
    :   Sync permanent error at

    `sync_success_at: Any`
    :   Sync success at

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

    `user: Any`
    :   User

    `user_id: Any`
    :   User id

    `username: Any`
    :   Username

<a id="MailboxesArrayContainsCondition"></a>

`MailboxesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.MailboxesAnyValueFilter`
    :   The type of the None singleton.

<a id="MailboxesContainsCondition"></a>

`MailboxesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.MailboxesAnyValueFilter`
    :   The type of the None singleton.

<a id="MailboxesEndswithCondition"></a>

`MailboxesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.MailboxesStringFilter`
    :   The type of the None singleton.

<a id="MailboxesEqCondition"></a>

`MailboxesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.MailboxesSearchFilter`
    :   The type of the None singleton.

<a id="MailboxesFuzzyCondition"></a>

`MailboxesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.MailboxesStringFilter`
    :   The type of the None singleton.

<a id="MailboxesGetParams"></a>

`MailboxesGetParams(*args, **kwargs)`
:   Parameters for mailboxes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="MailboxesGtCondition"></a>

`MailboxesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.MailboxesSearchFilter`
    :   The type of the None singleton.

<a id="MailboxesGteCondition"></a>

`MailboxesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.MailboxesSearchFilter`
    :   The type of the None singleton.

<a id="MailboxesInCondition"></a>

`MailboxesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.MailboxesInFilter`
    :   The type of the None singleton.

<a id="MailboxesInFilter"></a>

`MailboxesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auth_id: list[int]`
    :   Auth id

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `editable: list[bool]`
    :   Editable

    `email: list[str]`
    :   Email

    `email_hash: list[str]`
    :   Email hash

    `email_provider: list[str]`
    :   Email provider

    `email_signature: list[str]`
    :   Email signature

    `ews_custom_search_folder: list[bool]`
    :   Ews custom search folder

    `ews_delegate_sync: list[bool]`
    :   Ews delegate sync

    `ews_endpoint: list[str]`
    :   Ews endpoint

    `ews_impersonation: list[bool]`
    :   Ews impersonation

    `ews_ssl_verify_mode: list[int]`
    :   Ews ssl verify mode

    `exchange_version: list[str]`
    :   Exchange version

    `id: list[int]`
    :   Unique mailbox identifier

    `imap_host: list[str]`
    :   Imap host

    `imap_port: list[int]`
    :   Imap port

    `imap_ssl: list[bool]`
    :   Imap ssl

    `mail_aliases: list[list[typing.Any]]`
    :   Mail aliases

    `mailings: list[list[typing.Any]]`
    :   Mailings

    `max_emails_per_day: list[int]`
    :   Max emails per day

    `max_mailings_per_day: list[int]`
    :   Max mailings per day

    `max_mailings_per_week: list[int]`
    :   Max mailings per week

    `opt_out_message: list[str]`
    :   Opt out message

    `opt_out_signature: list[str]`
    :   Opt out signature

    `prospect_email_exclusions: list[list[typing.Any]]`
    :   Prospect email exclusions

    `provider_id: list[int]`
    :   Provider id

    `provider_type: list[str]`
    :   Provider type

    `send_disabled: list[bool]`
    :   Send disabled

    `send_errored_at: list[str]`
    :   Send errored at

    `send_max_retries: list[int]`
    :   Send max retries

    `send_method: list[str]`
    :   Send method

    `send_period: list[int]`
    :   Send period

    `send_permanent_error_at: list[str]`
    :   Send permanent error at

    `send_requires_sync: list[bool]`
    :   Send requires sync

    `send_success_at: list[str]`
    :   Send success at

    `send_threshold: list[int]`
    :   Send threshold

    `sendgrid_webhook_url: list[str]`
    :   Sendgrid webhook url

    `smtp_host: list[str]`
    :   Smtp host

    `smtp_port: list[int]`
    :   Smtp port

    `smtp_ssl: list[bool]`
    :   Smtp ssl

    `smtp_username: list[str]`
    :   Smtp username

    `sync_active_frequency: list[int]`
    :   Sync active frequency

    `sync_disabled: list[bool]`
    :   Sync disabled

    `sync_errored_at: list[str]`
    :   Sync errored at

    `sync_finished_at: list[str]`
    :   Sync finished at

    `sync_method: list[str]`
    :   Sync method

    `sync_outreach_folder: list[bool]`
    :   Sync outreach folder

    `sync_passive_frequency: list[int]`
    :   Sync passive frequency

    `sync_permanent_error_at: list[str]`
    :   Sync permanent error at

    `sync_success_at: list[str]`
    :   Sync success at

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

    `user: list[list[typing.Any]]`
    :   User

    `user_id: list[int]`
    :   User id

    `username: list[str]`
    :   Username

<a id="MailboxesKeywordCondition"></a>

`MailboxesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.MailboxesStringFilter`
    :   The type of the None singleton.

<a id="MailboxesListParams"></a>

`MailboxesListParams(*args, **kwargs)`
:   Parameters for mailboxes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="MailboxesLtCondition"></a>

`MailboxesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.MailboxesSearchFilter`
    :   The type of the None singleton.

<a id="MailboxesLteCondition"></a>

`MailboxesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.MailboxesSearchFilter`
    :   The type of the None singleton.

<a id="MailboxesNeqCondition"></a>

`MailboxesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.MailboxesSearchFilter`
    :   The type of the None singleton.

<a id="MailboxesNotCondition"></a>

`MailboxesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.MailboxesEqCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesGtCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesGteCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesLtCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesLteCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesInCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesNotCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesAndCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesOrCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesAnyCondition`
    :   The type of the None singleton.

<a id="MailboxesOrCondition"></a>

`MailboxesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.MailboxesEqCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesGtCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesGteCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesLtCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesLteCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesInCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesNotCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesAndCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesOrCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesAnyCondition]`
    :   The type of the None singleton.

<a id="MailboxesSearchFilter"></a>

`MailboxesSearchFilter(*args, **kwargs)`
:   Available fields for filtering mailboxes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="MailboxesSearchQuery"></a>

`MailboxesSearchQuery(*args, **kwargs)`
:   Search query for mailboxes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.MailboxesEqCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesGtCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesGteCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesLtCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesLteCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesInCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesNotCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesAndCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesOrCondition | airbyte_agent_sdk.connectors.outreach.types.MailboxesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.MailboxesSortFilter]`
    :   The type of the None singleton.

<a id="MailboxesSortFilter"></a>

`MailboxesSortFilter(*args, **kwargs)`
:   Available fields for sorting mailboxes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auth_id: Literal['asc', 'desc']`
    :   Auth id

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `editable: Literal['asc', 'desc']`
    :   Editable

    `email: Literal['asc', 'desc']`
    :   Email

    `email_hash: Literal['asc', 'desc']`
    :   Email hash

    `email_provider: Literal['asc', 'desc']`
    :   Email provider

    `email_signature: Literal['asc', 'desc']`
    :   Email signature

    `ews_custom_search_folder: Literal['asc', 'desc']`
    :   Ews custom search folder

    `ews_delegate_sync: Literal['asc', 'desc']`
    :   Ews delegate sync

    `ews_endpoint: Literal['asc', 'desc']`
    :   Ews endpoint

    `ews_impersonation: Literal['asc', 'desc']`
    :   Ews impersonation

    `ews_ssl_verify_mode: Literal['asc', 'desc']`
    :   Ews ssl verify mode

    `exchange_version: Literal['asc', 'desc']`
    :   Exchange version

    `id: Literal['asc', 'desc']`
    :   Unique mailbox identifier

    `imap_host: Literal['asc', 'desc']`
    :   Imap host

    `imap_port: Literal['asc', 'desc']`
    :   Imap port

    `imap_ssl: Literal['asc', 'desc']`
    :   Imap ssl

    `mail_aliases: Literal['asc', 'desc']`
    :   Mail aliases

    `mailings: Literal['asc', 'desc']`
    :   Mailings

    `max_emails_per_day: Literal['asc', 'desc']`
    :   Max emails per day

    `max_mailings_per_day: Literal['asc', 'desc']`
    :   Max mailings per day

    `max_mailings_per_week: Literal['asc', 'desc']`
    :   Max mailings per week

    `opt_out_message: Literal['asc', 'desc']`
    :   Opt out message

    `opt_out_signature: Literal['asc', 'desc']`
    :   Opt out signature

    `prospect_email_exclusions: Literal['asc', 'desc']`
    :   Prospect email exclusions

    `provider_id: Literal['asc', 'desc']`
    :   Provider id

    `provider_type: Literal['asc', 'desc']`
    :   Provider type

    `send_disabled: Literal['asc', 'desc']`
    :   Send disabled

    `send_errored_at: Literal['asc', 'desc']`
    :   Send errored at

    `send_max_retries: Literal['asc', 'desc']`
    :   Send max retries

    `send_method: Literal['asc', 'desc']`
    :   Send method

    `send_period: Literal['asc', 'desc']`
    :   Send period

    `send_permanent_error_at: Literal['asc', 'desc']`
    :   Send permanent error at

    `send_requires_sync: Literal['asc', 'desc']`
    :   Send requires sync

    `send_success_at: Literal['asc', 'desc']`
    :   Send success at

    `send_threshold: Literal['asc', 'desc']`
    :   Send threshold

    `sendgrid_webhook_url: Literal['asc', 'desc']`
    :   Sendgrid webhook url

    `smtp_host: Literal['asc', 'desc']`
    :   Smtp host

    `smtp_port: Literal['asc', 'desc']`
    :   Smtp port

    `smtp_ssl: Literal['asc', 'desc']`
    :   Smtp ssl

    `smtp_username: Literal['asc', 'desc']`
    :   Smtp username

    `sync_active_frequency: Literal['asc', 'desc']`
    :   Sync active frequency

    `sync_disabled: Literal['asc', 'desc']`
    :   Sync disabled

    `sync_errored_at: Literal['asc', 'desc']`
    :   Sync errored at

    `sync_finished_at: Literal['asc', 'desc']`
    :   Sync finished at

    `sync_method: Literal['asc', 'desc']`
    :   Sync method

    `sync_outreach_folder: Literal['asc', 'desc']`
    :   Sync outreach folder

    `sync_passive_frequency: Literal['asc', 'desc']`
    :   Sync passive frequency

    `sync_permanent_error_at: Literal['asc', 'desc']`
    :   Sync permanent error at

    `sync_success_at: Literal['asc', 'desc']`
    :   Sync success at

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

    `user: Literal['asc', 'desc']`
    :   User

    `user_id: Literal['asc', 'desc']`
    :   User id

    `username: Literal['asc', 'desc']`
    :   Username

<a id="MailboxesStartswithCondition"></a>

`MailboxesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.MailboxesStringFilter`
    :   The type of the None singleton.

<a id="MailboxesStringFilter"></a>

`MailboxesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auth_id: str`
    :   Auth id

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `editable: str`
    :   Editable

    `email: str`
    :   Email

    `email_hash: str`
    :   Email hash

    `email_provider: str`
    :   Email provider

    `email_signature: str`
    :   Email signature

    `ews_custom_search_folder: str`
    :   Ews custom search folder

    `ews_delegate_sync: str`
    :   Ews delegate sync

    `ews_endpoint: str`
    :   Ews endpoint

    `ews_impersonation: str`
    :   Ews impersonation

    `ews_ssl_verify_mode: str`
    :   Ews ssl verify mode

    `exchange_version: str`
    :   Exchange version

    `id: str`
    :   Unique mailbox identifier

    `imap_host: str`
    :   Imap host

    `imap_port: str`
    :   Imap port

    `imap_ssl: str`
    :   Imap ssl

    `mail_aliases: str`
    :   Mail aliases

    `mailings: str`
    :   Mailings

    `max_emails_per_day: str`
    :   Max emails per day

    `max_mailings_per_day: str`
    :   Max mailings per day

    `max_mailings_per_week: str`
    :   Max mailings per week

    `opt_out_message: str`
    :   Opt out message

    `opt_out_signature: str`
    :   Opt out signature

    `prospect_email_exclusions: str`
    :   Prospect email exclusions

    `provider_id: str`
    :   Provider id

    `provider_type: str`
    :   Provider type

    `send_disabled: str`
    :   Send disabled

    `send_errored_at: str`
    :   Send errored at

    `send_max_retries: str`
    :   Send max retries

    `send_method: str`
    :   Send method

    `send_period: str`
    :   Send period

    `send_permanent_error_at: str`
    :   Send permanent error at

    `send_requires_sync: str`
    :   Send requires sync

    `send_success_at: str`
    :   Send success at

    `send_threshold: str`
    :   Send threshold

    `sendgrid_webhook_url: str`
    :   Sendgrid webhook url

    `smtp_host: str`
    :   Smtp host

    `smtp_port: str`
    :   Smtp port

    `smtp_ssl: str`
    :   Smtp ssl

    `smtp_username: str`
    :   Smtp username

    `sync_active_frequency: str`
    :   Sync active frequency

    `sync_disabled: str`
    :   Sync disabled

    `sync_errored_at: str`
    :   Sync errored at

    `sync_finished_at: str`
    :   Sync finished at

    `sync_method: str`
    :   Sync method

    `sync_outreach_folder: str`
    :   Sync outreach folder

    `sync_passive_frequency: str`
    :   Sync passive frequency

    `sync_permanent_error_at: str`
    :   Sync permanent error at

    `sync_success_at: str`
    :   Sync success at

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

    `user: str`
    :   User

    `user_id: str`
    :   User id

    `username: str`
    :   Username

<a id="MailingsAndCondition"></a>

`MailingsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.MailingsEqCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsGtCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsGteCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsLtCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsLteCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsInCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsNotCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsAndCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsOrCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsAnyCondition]`
    :   The type of the None singleton.

<a id="MailingsAnyCondition"></a>

`MailingsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.MailingsAnyValueFilter`
    :   The type of the None singleton.

<a id="MailingsAnyValueFilter"></a>

`MailingsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: Any`
    :   Attachments

    `attributable_sequence_id: Any`
    :   Attributable sequence id

    `attributable_sequence_name: Any`
    :   Attributable sequence name

    `body_html: Any`
    :   Body html

    `body_text: Any`
    :   Body text

    `bounced_at: Any`
    :   Bounced at

    `calendar: Any`
    :   Calendar

    `click_count: Any`
    :   Click count

    `clicked_at: Any`
    :   Clicked at

    `created_at: Any`
    :   Created at

    `delivered_at: Any`
    :   Delivered at

    `desired_at: Any`
    :   Desired at

    `error_backtrace: Any`
    :   Error backtrace

    `error_reason: Any`
    :   Error reason

    `follow_up_sequence: Any`
    :   Follow up sequence

    `follow_up_sequence_id: Any`
    :   Follow up sequence id

    `follow_up_sequence_name: Any`
    :   Follow up sequence name

    `follow_up_sequence_starting_date: Any`
    :   Follow up sequence starting date

    `follow_up_task_scheduled_at: Any`
    :   Follow up task scheduled at

    `follow_up_task_type: Any`
    :   Follow up task type

    `id: Any`
    :   Unique mailing identifier

    `mailbox: Any`
    :   Mailbox

    `mailbox_address: Any`
    :   Mailbox address

    `mailing_type: Any`
    :   Mailing type

    `marked_as_spam_at: Any`
    :   Marked as spam at

    `meeting_description: Any`
    :   Meeting description

    `meeting_duration: Any`
    :   Meeting duration

    `meeting_location: Any`
    :   Meeting location

    `meeting_title: Any`
    :   Meeting title

    `message_id: Any`
    :   Message id

    `notify_thread_condition: Any`
    :   Notify thread condition

    `notify_thread_scheduled_at: Any`
    :   Notify thread scheduled at

    `notify_thread_status: Any`
    :   Notify thread status

    `open_count: Any`
    :   Open count

    `opened_at: Any`
    :   Opened at

    `opportunity: Any`
    :   Opportunity

    `optimized_scheduled_at: Any`
    :   Optimized scheduled at

    `override_safety_settings: Any`
    :   Override safety settings

    `prospect: Any`
    :   Prospect

    `recipients: Any`
    :   Recipients

    `references: Any`
    :   References

    `replied_at: Any`
    :   Replied at

    `reply_sentiment: Any`
    :   Reply sentiment

    `retry_at: Any`
    :   Retry at

    `retry_count: Any`
    :   Retry count

    `retry_interval: Any`
    :   Retry interval

    `schedule: Any`
    :   Schedule

    `schedule_id: Any`
    :   Schedule id

    `scheduled_at: Any`
    :   Scheduled at

    `sequence: Any`
    :   Sequence

    `sequence_state: Any`
    :   Sequence state

    `sequence_step: Any`
    :   Sequence step

    `state: Any`
    :   State

    `state_changed_at: Any`
    :   State changed at

    `subject: Any`
    :   Subject

    `task: Any`
    :   Task

    `tasks: Any`
    :   Tasks

    `template: Any`
    :   Template

    `track_links: Any`
    :   Track links

    `track_opens: Any`
    :   Track opens

    `unsubscribed_at: Any`
    :   Unsubscribed at

    `updated_at: Any`
    :   Updated at

    `user: Any`
    :   User

<a id="MailingsArrayContainsCondition"></a>

`MailingsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.MailingsAnyValueFilter`
    :   The type of the None singleton.

<a id="MailingsContainsCondition"></a>

`MailingsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.MailingsAnyValueFilter`
    :   The type of the None singleton.

<a id="MailingsEndswithCondition"></a>

`MailingsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.MailingsStringFilter`
    :   The type of the None singleton.

<a id="MailingsEqCondition"></a>

`MailingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.MailingsSearchFilter`
    :   The type of the None singleton.

<a id="MailingsFuzzyCondition"></a>

`MailingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.MailingsStringFilter`
    :   The type of the None singleton.

<a id="MailingsGetParams"></a>

`MailingsGetParams(*args, **kwargs)`
:   Parameters for mailings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="MailingsGtCondition"></a>

`MailingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.MailingsSearchFilter`
    :   The type of the None singleton.

<a id="MailingsGteCondition"></a>

`MailingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.MailingsSearchFilter`
    :   The type of the None singleton.

<a id="MailingsInCondition"></a>

`MailingsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.MailingsInFilter`
    :   The type of the None singleton.

<a id="MailingsInFilter"></a>

`MailingsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: list[list[typing.Any]]`
    :   Attachments

    `attributable_sequence_id: list[int]`
    :   Attributable sequence id

    `attributable_sequence_name: list[str]`
    :   Attributable sequence name

    `body_html: list[str]`
    :   Body html

    `body_text: list[str]`
    :   Body text

    `bounced_at: list[str]`
    :   Bounced at

    `calendar: list[list[typing.Any]]`
    :   Calendar

    `click_count: list[int]`
    :   Click count

    `clicked_at: list[str]`
    :   Clicked at

    `created_at: list[str]`
    :   Created at

    `delivered_at: list[str]`
    :   Delivered at

    `desired_at: list[str]`
    :   Desired at

    `error_backtrace: list[str]`
    :   Error backtrace

    `error_reason: list[str]`
    :   Error reason

    `follow_up_sequence: list[list[typing.Any]]`
    :   Follow up sequence

    `follow_up_sequence_id: list[int]`
    :   Follow up sequence id

    `follow_up_sequence_name: list[str]`
    :   Follow up sequence name

    `follow_up_sequence_starting_date: list[str]`
    :   Follow up sequence starting date

    `follow_up_task_scheduled_at: list[str]`
    :   Follow up task scheduled at

    `follow_up_task_type: list[str]`
    :   Follow up task type

    `id: list[int]`
    :   Unique mailing identifier

    `mailbox: list[list[typing.Any]]`
    :   Mailbox

    `mailbox_address: list[str]`
    :   Mailbox address

    `mailing_type: list[str]`
    :   Mailing type

    `marked_as_spam_at: list[str]`
    :   Marked as spam at

    `meeting_description: list[str]`
    :   Meeting description

    `meeting_duration: list[int]`
    :   Meeting duration

    `meeting_location: list[str]`
    :   Meeting location

    `meeting_title: list[str]`
    :   Meeting title

    `message_id: list[str]`
    :   Message id

    `notify_thread_condition: list[str]`
    :   Notify thread condition

    `notify_thread_scheduled_at: list[str]`
    :   Notify thread scheduled at

    `notify_thread_status: list[str]`
    :   Notify thread status

    `open_count: list[int]`
    :   Open count

    `opened_at: list[str]`
    :   Opened at

    `opportunity: list[list[typing.Any]]`
    :   Opportunity

    `optimized_scheduled_at: list[str]`
    :   Optimized scheduled at

    `override_safety_settings: list[bool]`
    :   Override safety settings

    `prospect: list[list[typing.Any]]`
    :   Prospect

    `recipients: list[list[typing.Any]]`
    :   Recipients

    `references: list[list[typing.Any]]`
    :   References

    `replied_at: list[str]`
    :   Replied at

    `reply_sentiment: list[str]`
    :   Reply sentiment

    `retry_at: list[str]`
    :   Retry at

    `retry_count: list[int]`
    :   Retry count

    `retry_interval: list[int]`
    :   Retry interval

    `schedule: list[list[typing.Any]]`
    :   Schedule

    `schedule_id: list[int]`
    :   Schedule id

    `scheduled_at: list[str]`
    :   Scheduled at

    `sequence: list[list[typing.Any]]`
    :   Sequence

    `sequence_state: list[list[typing.Any]]`
    :   Sequence state

    `sequence_step: list[list[typing.Any]]`
    :   Sequence step

    `state: list[str]`
    :   State

    `state_changed_at: list[str]`
    :   State changed at

    `subject: list[str]`
    :   Subject

    `task: list[list[typing.Any]]`
    :   Task

    `tasks: list[list[typing.Any]]`
    :   Tasks

    `template: list[list[typing.Any]]`
    :   Template

    `track_links: list[bool]`
    :   Track links

    `track_opens: list[bool]`
    :   Track opens

    `unsubscribed_at: list[str]`
    :   Unsubscribed at

    `updated_at: list[str]`
    :   Updated at

    `user: list[list[typing.Any]]`
    :   User

<a id="MailingsKeywordCondition"></a>

`MailingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.MailingsStringFilter`
    :   The type of the None singleton.

<a id="MailingsListParams"></a>

`MailingsListParams(*args, **kwargs)`
:   Parameters for mailings.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="MailingsLtCondition"></a>

`MailingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.MailingsSearchFilter`
    :   The type of the None singleton.

<a id="MailingsLteCondition"></a>

`MailingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.MailingsSearchFilter`
    :   The type of the None singleton.

<a id="MailingsNeqCondition"></a>

`MailingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.MailingsSearchFilter`
    :   The type of the None singleton.

<a id="MailingsNotCondition"></a>

`MailingsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.MailingsEqCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsGtCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsGteCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsLtCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsLteCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsInCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsNotCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsAndCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsOrCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsAnyCondition`
    :   The type of the None singleton.

<a id="MailingsOrCondition"></a>

`MailingsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.MailingsEqCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsGtCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsGteCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsLtCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsLteCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsInCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsNotCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsAndCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsOrCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsAnyCondition]`
    :   The type of the None singleton.

<a id="MailingsSearchFilter"></a>

`MailingsSearchFilter(*args, **kwargs)`
:   Available fields for filtering mailings search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="MailingsSearchQuery"></a>

`MailingsSearchQuery(*args, **kwargs)`
:   Search query for mailings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.MailingsEqCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsGtCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsGteCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsLtCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsLteCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsInCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsNotCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsAndCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsOrCondition | airbyte_agent_sdk.connectors.outreach.types.MailingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.MailingsSortFilter]`
    :   The type of the None singleton.

<a id="MailingsSortFilter"></a>

`MailingsSortFilter(*args, **kwargs)`
:   Available fields for sorting mailings search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: Literal['asc', 'desc']`
    :   Attachments

    `attributable_sequence_id: Literal['asc', 'desc']`
    :   Attributable sequence id

    `attributable_sequence_name: Literal['asc', 'desc']`
    :   Attributable sequence name

    `body_html: Literal['asc', 'desc']`
    :   Body html

    `body_text: Literal['asc', 'desc']`
    :   Body text

    `bounced_at: Literal['asc', 'desc']`
    :   Bounced at

    `calendar: Literal['asc', 'desc']`
    :   Calendar

    `click_count: Literal['asc', 'desc']`
    :   Click count

    `clicked_at: Literal['asc', 'desc']`
    :   Clicked at

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `delivered_at: Literal['asc', 'desc']`
    :   Delivered at

    `desired_at: Literal['asc', 'desc']`
    :   Desired at

    `error_backtrace: Literal['asc', 'desc']`
    :   Error backtrace

    `error_reason: Literal['asc', 'desc']`
    :   Error reason

    `follow_up_sequence: Literal['asc', 'desc']`
    :   Follow up sequence

    `follow_up_sequence_id: Literal['asc', 'desc']`
    :   Follow up sequence id

    `follow_up_sequence_name: Literal['asc', 'desc']`
    :   Follow up sequence name

    `follow_up_sequence_starting_date: Literal['asc', 'desc']`
    :   Follow up sequence starting date

    `follow_up_task_scheduled_at: Literal['asc', 'desc']`
    :   Follow up task scheduled at

    `follow_up_task_type: Literal['asc', 'desc']`
    :   Follow up task type

    `id: Literal['asc', 'desc']`
    :   Unique mailing identifier

    `mailbox: Literal['asc', 'desc']`
    :   Mailbox

    `mailbox_address: Literal['asc', 'desc']`
    :   Mailbox address

    `mailing_type: Literal['asc', 'desc']`
    :   Mailing type

    `marked_as_spam_at: Literal['asc', 'desc']`
    :   Marked as spam at

    `meeting_description: Literal['asc', 'desc']`
    :   Meeting description

    `meeting_duration: Literal['asc', 'desc']`
    :   Meeting duration

    `meeting_location: Literal['asc', 'desc']`
    :   Meeting location

    `meeting_title: Literal['asc', 'desc']`
    :   Meeting title

    `message_id: Literal['asc', 'desc']`
    :   Message id

    `notify_thread_condition: Literal['asc', 'desc']`
    :   Notify thread condition

    `notify_thread_scheduled_at: Literal['asc', 'desc']`
    :   Notify thread scheduled at

    `notify_thread_status: Literal['asc', 'desc']`
    :   Notify thread status

    `open_count: Literal['asc', 'desc']`
    :   Open count

    `opened_at: Literal['asc', 'desc']`
    :   Opened at

    `opportunity: Literal['asc', 'desc']`
    :   Opportunity

    `optimized_scheduled_at: Literal['asc', 'desc']`
    :   Optimized scheduled at

    `override_safety_settings: Literal['asc', 'desc']`
    :   Override safety settings

    `prospect: Literal['asc', 'desc']`
    :   Prospect

    `recipients: Literal['asc', 'desc']`
    :   Recipients

    `references: Literal['asc', 'desc']`
    :   References

    `replied_at: Literal['asc', 'desc']`
    :   Replied at

    `reply_sentiment: Literal['asc', 'desc']`
    :   Reply sentiment

    `retry_at: Literal['asc', 'desc']`
    :   Retry at

    `retry_count: Literal['asc', 'desc']`
    :   Retry count

    `retry_interval: Literal['asc', 'desc']`
    :   Retry interval

    `schedule: Literal['asc', 'desc']`
    :   Schedule

    `schedule_id: Literal['asc', 'desc']`
    :   Schedule id

    `scheduled_at: Literal['asc', 'desc']`
    :   Scheduled at

    `sequence: Literal['asc', 'desc']`
    :   Sequence

    `sequence_state: Literal['asc', 'desc']`
    :   Sequence state

    `sequence_step: Literal['asc', 'desc']`
    :   Sequence step

    `state: Literal['asc', 'desc']`
    :   State

    `state_changed_at: Literal['asc', 'desc']`
    :   State changed at

    `subject: Literal['asc', 'desc']`
    :   Subject

    `task: Literal['asc', 'desc']`
    :   Task

    `tasks: Literal['asc', 'desc']`
    :   Tasks

    `template: Literal['asc', 'desc']`
    :   Template

    `track_links: Literal['asc', 'desc']`
    :   Track links

    `track_opens: Literal['asc', 'desc']`
    :   Track opens

    `unsubscribed_at: Literal['asc', 'desc']`
    :   Unsubscribed at

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `user: Literal['asc', 'desc']`
    :   User

<a id="MailingsStartswithCondition"></a>

`MailingsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.MailingsStringFilter`
    :   The type of the None singleton.

<a id="MailingsStringFilter"></a>

`MailingsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: str`
    :   Attachments

    `attributable_sequence_id: str`
    :   Attributable sequence id

    `attributable_sequence_name: str`
    :   Attributable sequence name

    `body_html: str`
    :   Body html

    `body_text: str`
    :   Body text

    `bounced_at: str`
    :   Bounced at

    `calendar: str`
    :   Calendar

    `click_count: str`
    :   Click count

    `clicked_at: str`
    :   Clicked at

    `created_at: str`
    :   Created at

    `delivered_at: str`
    :   Delivered at

    `desired_at: str`
    :   Desired at

    `error_backtrace: str`
    :   Error backtrace

    `error_reason: str`
    :   Error reason

    `follow_up_sequence: str`
    :   Follow up sequence

    `follow_up_sequence_id: str`
    :   Follow up sequence id

    `follow_up_sequence_name: str`
    :   Follow up sequence name

    `follow_up_sequence_starting_date: str`
    :   Follow up sequence starting date

    `follow_up_task_scheduled_at: str`
    :   Follow up task scheduled at

    `follow_up_task_type: str`
    :   Follow up task type

    `id: str`
    :   Unique mailing identifier

    `mailbox: str`
    :   Mailbox

    `mailbox_address: str`
    :   Mailbox address

    `mailing_type: str`
    :   Mailing type

    `marked_as_spam_at: str`
    :   Marked as spam at

    `meeting_description: str`
    :   Meeting description

    `meeting_duration: str`
    :   Meeting duration

    `meeting_location: str`
    :   Meeting location

    `meeting_title: str`
    :   Meeting title

    `message_id: str`
    :   Message id

    `notify_thread_condition: str`
    :   Notify thread condition

    `notify_thread_scheduled_at: str`
    :   Notify thread scheduled at

    `notify_thread_status: str`
    :   Notify thread status

    `open_count: str`
    :   Open count

    `opened_at: str`
    :   Opened at

    `opportunity: str`
    :   Opportunity

    `optimized_scheduled_at: str`
    :   Optimized scheduled at

    `override_safety_settings: str`
    :   Override safety settings

    `prospect: str`
    :   Prospect

    `recipients: str`
    :   Recipients

    `references: str`
    :   References

    `replied_at: str`
    :   Replied at

    `reply_sentiment: str`
    :   Reply sentiment

    `retry_at: str`
    :   Retry at

    `retry_count: str`
    :   Retry count

    `retry_interval: str`
    :   Retry interval

    `schedule: str`
    :   Schedule

    `schedule_id: str`
    :   Schedule id

    `scheduled_at: str`
    :   Scheduled at

    `sequence: str`
    :   Sequence

    `sequence_state: str`
    :   Sequence state

    `sequence_step: str`
    :   Sequence step

    `state: str`
    :   State

    `state_changed_at: str`
    :   State changed at

    `subject: str`
    :   Subject

    `task: str`
    :   Task

    `tasks: str`
    :   Tasks

    `template: str`
    :   Template

    `track_links: str`
    :   Track links

    `track_opens: str`
    :   Track opens

    `unsubscribed_at: str`
    :   Unsubscribed at

    `updated_at: str`
    :   Updated at

    `user: str`
    :   User

<a id="OpportunitiesAndCondition"></a>

`OpportunitiesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.OpportunitiesEqCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesGtCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesGteCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesLtCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesLteCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesInCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesNotCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAndCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesOrCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAnyCondition]`
    :   The type of the None singleton.

<a id="OpportunitiesAnyCondition"></a>

`OpportunitiesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAnyValueFilter`
    :   The type of the None singleton.

<a id="OpportunitiesAnyValueFilter"></a>

`OpportunitiesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Any`
    :   Account

    `amount: Any`
    :   Amount

    `assigned_teams: Any`
    :   Assigned teams

    `assigned_users: Any`
    :   Assigned users

    `close_date: Any`
    :   Close date

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `currency_type: Any`
    :   Currency type

    `custom1: Any`
    :   Custom field 1

    `custom10: Any`
    :   Custom field 10

    `custom100: Any`
    :   Custom field 100

    `custom101: Any`
    :   Custom field 101

    `custom102: Any`
    :   Custom field 102

    `custom103: Any`
    :   Custom field 103

    `custom104: Any`
    :   Custom field 104

    `custom105: Any`
    :   Custom field 105

    `custom106: Any`
    :   Custom field 106

    `custom107: Any`
    :   Custom field 107

    `custom108: Any`
    :   Custom field 108

    `custom109: Any`
    :   Custom field 109

    `custom11: Any`
    :   Custom field 11

    `custom110: Any`
    :   Custom field 110

    `custom111: Any`
    :   Custom field 111

    `custom112: Any`
    :   Custom field 112

    `custom113: Any`
    :   Custom field 113

    `custom114: Any`
    :   Custom field 114

    `custom115: Any`
    :   Custom field 115

    `custom116: Any`
    :   Custom field 116

    `custom117: Any`
    :   Custom field 117

    `custom118: Any`
    :   Custom field 118

    `custom119: Any`
    :   Custom field 119

    `custom12: Any`
    :   Custom field 12

    `custom120: Any`
    :   Custom field 120

    `custom121: Any`
    :   Custom field 121

    `custom122: Any`
    :   Custom field 122

    `custom123: Any`
    :   Custom field 123

    `custom124: Any`
    :   Custom field 124

    `custom125: Any`
    :   Custom field 125

    `custom126: Any`
    :   Custom field 126

    `custom127: Any`
    :   Custom field 127

    `custom128: Any`
    :   Custom field 128

    `custom129: Any`
    :   Custom field 129

    `custom13: Any`
    :   Custom field 13

    `custom130: Any`
    :   Custom field 130

    `custom131: Any`
    :   Custom field 131

    `custom132: Any`
    :   Custom field 132

    `custom133: Any`
    :   Custom field 133

    `custom134: Any`
    :   Custom field 134

    `custom135: Any`
    :   Custom field 135

    `custom136: Any`
    :   Custom field 136

    `custom137: Any`
    :   Custom field 137

    `custom138: Any`
    :   Custom field 138

    `custom139: Any`
    :   Custom field 139

    `custom14: Any`
    :   Custom field 14

    `custom140: Any`
    :   Custom field 140

    `custom141: Any`
    :   Custom field 141

    `custom142: Any`
    :   Custom field 142

    `custom143: Any`
    :   Custom field 143

    `custom144: Any`
    :   Custom field 144

    `custom145: Any`
    :   Custom field 145

    `custom146: Any`
    :   Custom field 146

    `custom147: Any`
    :   Custom field 147

    `custom148: Any`
    :   Custom field 148

    `custom149: Any`
    :   Custom field 149

    `custom15: Any`
    :   Custom field 15

    `custom150: Any`
    :   Custom field 150

    `custom16: Any`
    :   Custom field 16

    `custom17: Any`
    :   Custom field 17

    `custom18: Any`
    :   Custom field 18

    `custom19: Any`
    :   Custom field 19

    `custom2: Any`
    :   Custom field 2

    `custom20: Any`
    :   Custom field 20

    `custom21: Any`
    :   Custom field 21

    `custom22: Any`
    :   Custom field 22

    `custom23: Any`
    :   Custom field 23

    `custom24: Any`
    :   Custom field 24

    `custom25: Any`
    :   Custom field 25

    `custom26: Any`
    :   Custom field 26

    `custom27: Any`
    :   Custom field 27

    `custom28: Any`
    :   Custom field 28

    `custom29: Any`
    :   Custom field 29

    `custom3: Any`
    :   Custom field 3

    `custom30: Any`
    :   Custom field 30

    `custom31: Any`
    :   Custom field 31

    `custom32: Any`
    :   Custom field 32

    `custom33: Any`
    :   Custom field 33

    `custom34: Any`
    :   Custom field 34

    `custom35: Any`
    :   Custom field 35

    `custom36: Any`
    :   Custom field 36

    `custom37: Any`
    :   Custom field 37

    `custom38: Any`
    :   Custom field 38

    `custom39: Any`
    :   Custom field 39

    `custom4: Any`
    :   Custom field 4

    `custom40: Any`
    :   Custom field 40

    `custom41: Any`
    :   Custom field 41

    `custom42: Any`
    :   Custom field 42

    `custom43: Any`
    :   Custom field 43

    `custom44: Any`
    :   Custom field 44

    `custom45: Any`
    :   Custom field 45

    `custom46: Any`
    :   Custom field 46

    `custom47: Any`
    :   Custom field 47

    `custom48: Any`
    :   Custom field 48

    `custom49: Any`
    :   Custom field 49

    `custom5: Any`
    :   Custom field 5

    `custom50: Any`
    :   Custom field 50

    `custom51: Any`
    :   Custom field 51

    `custom52: Any`
    :   Custom field 52

    `custom53: Any`
    :   Custom field 53

    `custom54: Any`
    :   Custom field 54

    `custom55: Any`
    :   Custom field 55

    `custom56: Any`
    :   Custom field 56

    `custom57: Any`
    :   Custom field 57

    `custom58: Any`
    :   Custom field 58

    `custom59: Any`
    :   Custom field 59

    `custom6: Any`
    :   Custom field 6

    `custom60: Any`
    :   Custom field 60

    `custom61: Any`
    :   Custom field 61

    `custom62: Any`
    :   Custom field 62

    `custom63: Any`
    :   Custom field 63

    `custom64: Any`
    :   Custom field 64

    `custom65: Any`
    :   Custom field 65

    `custom66: Any`
    :   Custom field 66

    `custom67: Any`
    :   Custom field 67

    `custom68: Any`
    :   Custom field 68

    `custom69: Any`
    :   Custom field 69

    `custom7: Any`
    :   Custom field 7

    `custom70: Any`
    :   Custom field 70

    `custom71: Any`
    :   Custom field 71

    `custom72: Any`
    :   Custom field 72

    `custom73: Any`
    :   Custom field 73

    `custom74: Any`
    :   Custom field 74

    `custom75: Any`
    :   Custom field 75

    `custom76: Any`
    :   Custom field 76

    `custom77: Any`
    :   Custom field 77

    `custom78: Any`
    :   Custom field 78

    `custom79: Any`
    :   Custom field 79

    `custom8: Any`
    :   Custom field 8

    `custom80: Any`
    :   Custom field 80

    `custom81: Any`
    :   Custom field 81

    `custom82: Any`
    :   Custom field 82

    `custom83: Any`
    :   Custom field 83

    `custom84: Any`
    :   Custom field 84

    `custom85: Any`
    :   Custom field 85

    `custom86: Any`
    :   Custom field 86

    `custom87: Any`
    :   Custom field 87

    `custom88: Any`
    :   Custom field 88

    `custom89: Any`
    :   Custom field 89

    `custom9: Any`
    :   Custom field 9

    `custom90: Any`
    :   Custom field 90

    `custom91: Any`
    :   Custom field 91

    `custom92: Any`
    :   Custom field 92

    `custom93: Any`
    :   Custom field 93

    `custom94: Any`
    :   Custom field 94

    `custom95: Any`
    :   Custom field 95

    `custom96: Any`
    :   Custom field 96

    `custom97: Any`
    :   Custom field 97

    `custom98: Any`
    :   Custom field 98

    `custom99: Any`
    :   Custom field 99

    `default_plugin_mapping: Any`
    :   Default plugin mapping

    `description: Any`
    :   Description

    `external_created_at: Any`
    :   External created at

    `external_creator: Any`
    :   External creator

    `favorites: Any`
    :   Favorites

    `health_category: Any`
    :   Health category

    `health_score: Any`
    :   Health score

    `id: Any`
    :   Unique opportunity identifier

    `map_link: Any`
    :   Map link

    `map_next_steps: Any`
    :   Map next steps

    `map_number_of_overdue_tasks: Any`
    :   Map number of overdue tasks

    `map_status: Any`
    :   Map status

    `name: Any`
    :   Name

    `next_step: Any`
    :   Next step

    `opportunity_health_factors: Any`
    :   Opportunity health factors

    `opportunity_stage: Any`
    :   Opportunity stage

    `opportunity_type: Any`
    :   Opportunity type

    `owner: Any`
    :   Owner

    `primary_prospect: Any`
    :   Primary prospect

    `probability: Any`
    :   Probability

    `prospecting_rep_id: Any`
    :   Prospecting rep id

    `prospects: Any`
    :   Prospects

    `sharing_team_id: Any`
    :   Sharing team id

    `stage: Any`
    :   Stage

    `tags: Any`
    :   Tags

    `touched_at: Any`
    :   Touched at

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

<a id="OpportunitiesArrayContainsCondition"></a>

`OpportunitiesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAnyValueFilter`
    :   The type of the None singleton.

<a id="OpportunitiesContainsCondition"></a>

`OpportunitiesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAnyValueFilter`
    :   The type of the None singleton.

<a id="OpportunitiesEndswithCondition"></a>

`OpportunitiesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesStringFilter`
    :   The type of the None singleton.

<a id="OpportunitiesEqCondition"></a>

`OpportunitiesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

<a id="OpportunitiesFuzzyCondition"></a>

`OpportunitiesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesStringFilter`
    :   The type of the None singleton.

<a id="OpportunitiesGetParams"></a>

`OpportunitiesGetParams(*args, **kwargs)`
:   Parameters for opportunities.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="OpportunitiesGtCondition"></a>

`OpportunitiesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

<a id="OpportunitiesGteCondition"></a>

`OpportunitiesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

<a id="OpportunitiesInCondition"></a>

`OpportunitiesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesInFilter`
    :   The type of the None singleton.

<a id="OpportunitiesInFilter"></a>

`OpportunitiesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: list[list[typing.Any]]`
    :   Account

    `amount: list[int]`
    :   Amount

    `assigned_teams: list[list[typing.Any]]`
    :   Assigned teams

    `assigned_users: list[list[typing.Any]]`
    :   Assigned users

    `close_date: list[str]`
    :   Close date

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `currency_type: list[str]`
    :   Currency type

    `custom1: list[str]`
    :   Custom field 1

    `custom10: list[str]`
    :   Custom field 10

    `custom100: list[str]`
    :   Custom field 100

    `custom101: list[str]`
    :   Custom field 101

    `custom102: list[str]`
    :   Custom field 102

    `custom103: list[str]`
    :   Custom field 103

    `custom104: list[str]`
    :   Custom field 104

    `custom105: list[str]`
    :   Custom field 105

    `custom106: list[str]`
    :   Custom field 106

    `custom107: list[str]`
    :   Custom field 107

    `custom108: list[str]`
    :   Custom field 108

    `custom109: list[str]`
    :   Custom field 109

    `custom11: list[str]`
    :   Custom field 11

    `custom110: list[str]`
    :   Custom field 110

    `custom111: list[str]`
    :   Custom field 111

    `custom112: list[str]`
    :   Custom field 112

    `custom113: list[str]`
    :   Custom field 113

    `custom114: list[str]`
    :   Custom field 114

    `custom115: list[str]`
    :   Custom field 115

    `custom116: list[str]`
    :   Custom field 116

    `custom117: list[str]`
    :   Custom field 117

    `custom118: list[str]`
    :   Custom field 118

    `custom119: list[str]`
    :   Custom field 119

    `custom12: list[str]`
    :   Custom field 12

    `custom120: list[str]`
    :   Custom field 120

    `custom121: list[str]`
    :   Custom field 121

    `custom122: list[str]`
    :   Custom field 122

    `custom123: list[str]`
    :   Custom field 123

    `custom124: list[str]`
    :   Custom field 124

    `custom125: list[str]`
    :   Custom field 125

    `custom126: list[str]`
    :   Custom field 126

    `custom127: list[str]`
    :   Custom field 127

    `custom128: list[str]`
    :   Custom field 128

    `custom129: list[str]`
    :   Custom field 129

    `custom13: list[str]`
    :   Custom field 13

    `custom130: list[str]`
    :   Custom field 130

    `custom131: list[str]`
    :   Custom field 131

    `custom132: list[str]`
    :   Custom field 132

    `custom133: list[str]`
    :   Custom field 133

    `custom134: list[str]`
    :   Custom field 134

    `custom135: list[str]`
    :   Custom field 135

    `custom136: list[str]`
    :   Custom field 136

    `custom137: list[str]`
    :   Custom field 137

    `custom138: list[str]`
    :   Custom field 138

    `custom139: list[str]`
    :   Custom field 139

    `custom14: list[str]`
    :   Custom field 14

    `custom140: list[str]`
    :   Custom field 140

    `custom141: list[str]`
    :   Custom field 141

    `custom142: list[str]`
    :   Custom field 142

    `custom143: list[str]`
    :   Custom field 143

    `custom144: list[str]`
    :   Custom field 144

    `custom145: list[str]`
    :   Custom field 145

    `custom146: list[str]`
    :   Custom field 146

    `custom147: list[str]`
    :   Custom field 147

    `custom148: list[str]`
    :   Custom field 148

    `custom149: list[str]`
    :   Custom field 149

    `custom15: list[str]`
    :   Custom field 15

    `custom150: list[str]`
    :   Custom field 150

    `custom16: list[str]`
    :   Custom field 16

    `custom17: list[str]`
    :   Custom field 17

    `custom18: list[str]`
    :   Custom field 18

    `custom19: list[str]`
    :   Custom field 19

    `custom2: list[str]`
    :   Custom field 2

    `custom20: list[str]`
    :   Custom field 20

    `custom21: list[str]`
    :   Custom field 21

    `custom22: list[str]`
    :   Custom field 22

    `custom23: list[str]`
    :   Custom field 23

    `custom24: list[str]`
    :   Custom field 24

    `custom25: list[str]`
    :   Custom field 25

    `custom26: list[str]`
    :   Custom field 26

    `custom27: list[str]`
    :   Custom field 27

    `custom28: list[str]`
    :   Custom field 28

    `custom29: list[str]`
    :   Custom field 29

    `custom3: list[str]`
    :   Custom field 3

    `custom30: list[str]`
    :   Custom field 30

    `custom31: list[str]`
    :   Custom field 31

    `custom32: list[str]`
    :   Custom field 32

    `custom33: list[str]`
    :   Custom field 33

    `custom34: list[str]`
    :   Custom field 34

    `custom35: list[str]`
    :   Custom field 35

    `custom36: list[str]`
    :   Custom field 36

    `custom37: list[str]`
    :   Custom field 37

    `custom38: list[str]`
    :   Custom field 38

    `custom39: list[str]`
    :   Custom field 39

    `custom4: list[str]`
    :   Custom field 4

    `custom40: list[str]`
    :   Custom field 40

    `custom41: list[str]`
    :   Custom field 41

    `custom42: list[str]`
    :   Custom field 42

    `custom43: list[str]`
    :   Custom field 43

    `custom44: list[str]`
    :   Custom field 44

    `custom45: list[str]`
    :   Custom field 45

    `custom46: list[str]`
    :   Custom field 46

    `custom47: list[str]`
    :   Custom field 47

    `custom48: list[str]`
    :   Custom field 48

    `custom49: list[str]`
    :   Custom field 49

    `custom5: list[str]`
    :   Custom field 5

    `custom50: list[str]`
    :   Custom field 50

    `custom51: list[str]`
    :   Custom field 51

    `custom52: list[str]`
    :   Custom field 52

    `custom53: list[str]`
    :   Custom field 53

    `custom54: list[str]`
    :   Custom field 54

    `custom55: list[str]`
    :   Custom field 55

    `custom56: list[str]`
    :   Custom field 56

    `custom57: list[str]`
    :   Custom field 57

    `custom58: list[str]`
    :   Custom field 58

    `custom59: list[str]`
    :   Custom field 59

    `custom6: list[str]`
    :   Custom field 6

    `custom60: list[str]`
    :   Custom field 60

    `custom61: list[str]`
    :   Custom field 61

    `custom62: list[str]`
    :   Custom field 62

    `custom63: list[str]`
    :   Custom field 63

    `custom64: list[str]`
    :   Custom field 64

    `custom65: list[str]`
    :   Custom field 65

    `custom66: list[str]`
    :   Custom field 66

    `custom67: list[str]`
    :   Custom field 67

    `custom68: list[str]`
    :   Custom field 68

    `custom69: list[str]`
    :   Custom field 69

    `custom7: list[str]`
    :   Custom field 7

    `custom70: list[str]`
    :   Custom field 70

    `custom71: list[str]`
    :   Custom field 71

    `custom72: list[str]`
    :   Custom field 72

    `custom73: list[str]`
    :   Custom field 73

    `custom74: list[str]`
    :   Custom field 74

    `custom75: list[str]`
    :   Custom field 75

    `custom76: list[str]`
    :   Custom field 76

    `custom77: list[str]`
    :   Custom field 77

    `custom78: list[str]`
    :   Custom field 78

    `custom79: list[str]`
    :   Custom field 79

    `custom8: list[str]`
    :   Custom field 8

    `custom80: list[str]`
    :   Custom field 80

    `custom81: list[str]`
    :   Custom field 81

    `custom82: list[str]`
    :   Custom field 82

    `custom83: list[str]`
    :   Custom field 83

    `custom84: list[str]`
    :   Custom field 84

    `custom85: list[str]`
    :   Custom field 85

    `custom86: list[str]`
    :   Custom field 86

    `custom87: list[str]`
    :   Custom field 87

    `custom88: list[str]`
    :   Custom field 88

    `custom89: list[str]`
    :   Custom field 89

    `custom9: list[str]`
    :   Custom field 9

    `custom90: list[str]`
    :   Custom field 90

    `custom91: list[str]`
    :   Custom field 91

    `custom92: list[str]`
    :   Custom field 92

    `custom93: list[str]`
    :   Custom field 93

    `custom94: list[str]`
    :   Custom field 94

    `custom95: list[str]`
    :   Custom field 95

    `custom96: list[str]`
    :   Custom field 96

    `custom97: list[str]`
    :   Custom field 97

    `custom98: list[str]`
    :   Custom field 98

    `custom99: list[str]`
    :   Custom field 99

    `default_plugin_mapping: list[list[typing.Any]]`
    :   Default plugin mapping

    `description: list[str]`
    :   Description

    `external_created_at: list[str]`
    :   External created at

    `external_creator: list[list[typing.Any]]`
    :   External creator

    `favorites: list[list[typing.Any]]`
    :   Favorites

    `health_category: list[str]`
    :   Health category

    `health_score: list[int]`
    :   Health score

    `id: list[int]`
    :   Unique opportunity identifier

    `map_link: list[str]`
    :   Map link

    `map_next_steps: list[str]`
    :   Map next steps

    `map_number_of_overdue_tasks: list[int]`
    :   Map number of overdue tasks

    `map_status: list[str]`
    :   Map status

    `name: list[str]`
    :   Name

    `next_step: list[str]`
    :   Next step

    `opportunity_health_factors: list[list[typing.Any]]`
    :   Opportunity health factors

    `opportunity_stage: list[list[typing.Any]]`
    :   Opportunity stage

    `opportunity_type: list[str]`
    :   Opportunity type

    `owner: list[list[typing.Any]]`
    :   Owner

    `primary_prospect: list[list[typing.Any]]`
    :   Primary prospect

    `probability: list[int]`
    :   Probability

    `prospecting_rep_id: list[str]`
    :   Prospecting rep id

    `prospects: list[list[typing.Any]]`
    :   Prospects

    `sharing_team_id: list[str]`
    :   Sharing team id

    `stage: list[list[typing.Any]]`
    :   Stage

    `tags: list[list[typing.Any]]`
    :   Tags

    `touched_at: list[str]`
    :   Touched at

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

<a id="OpportunitiesKeywordCondition"></a>

`OpportunitiesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesStringFilter`
    :   The type of the None singleton.

<a id="OpportunitiesListParams"></a>

`OpportunitiesListParams(*args, **kwargs)`
:   Parameters for opportunities.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="OpportunitiesLtCondition"></a>

`OpportunitiesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

<a id="OpportunitiesLteCondition"></a>

`OpportunitiesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

<a id="OpportunitiesNeqCondition"></a>

`OpportunitiesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

<a id="OpportunitiesNotCondition"></a>

`OpportunitiesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesEqCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesGtCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesGteCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesLtCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesLteCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesInCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesNotCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAndCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesOrCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAnyCondition`
    :   The type of the None singleton.

<a id="OpportunitiesOrCondition"></a>

`OpportunitiesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.OpportunitiesEqCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesGtCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesGteCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesLtCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesLteCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesInCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesNotCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAndCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesOrCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAnyCondition]`
    :   The type of the None singleton.

<a id="OpportunitiesSearchFilter"></a>

`OpportunitiesSearchFilter(*args, **kwargs)`
:   Available fields for filtering opportunities search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="OpportunitiesSearchQuery"></a>

`OpportunitiesSearchQuery(*args, **kwargs)`
:   Search query for opportunities entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesEqCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesGtCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesGteCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesLtCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesLteCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesInCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesNotCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAndCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesOrCondition | airbyte_agent_sdk.connectors.outreach.types.OpportunitiesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.OpportunitiesSortFilter]`
    :   The type of the None singleton.

<a id="OpportunitiesSortFilter"></a>

`OpportunitiesSortFilter(*args, **kwargs)`
:   Available fields for sorting opportunities search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Literal['asc', 'desc']`
    :   Account

    `amount: Literal['asc', 'desc']`
    :   Amount

    `assigned_teams: Literal['asc', 'desc']`
    :   Assigned teams

    `assigned_users: Literal['asc', 'desc']`
    :   Assigned users

    `close_date: Literal['asc', 'desc']`
    :   Close date

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `currency_type: Literal['asc', 'desc']`
    :   Currency type

    `custom1: Literal['asc', 'desc']`
    :   Custom field 1

    `custom10: Literal['asc', 'desc']`
    :   Custom field 10

    `custom100: Literal['asc', 'desc']`
    :   Custom field 100

    `custom101: Literal['asc', 'desc']`
    :   Custom field 101

    `custom102: Literal['asc', 'desc']`
    :   Custom field 102

    `custom103: Literal['asc', 'desc']`
    :   Custom field 103

    `custom104: Literal['asc', 'desc']`
    :   Custom field 104

    `custom105: Literal['asc', 'desc']`
    :   Custom field 105

    `custom106: Literal['asc', 'desc']`
    :   Custom field 106

    `custom107: Literal['asc', 'desc']`
    :   Custom field 107

    `custom108: Literal['asc', 'desc']`
    :   Custom field 108

    `custom109: Literal['asc', 'desc']`
    :   Custom field 109

    `custom11: Literal['asc', 'desc']`
    :   Custom field 11

    `custom110: Literal['asc', 'desc']`
    :   Custom field 110

    `custom111: Literal['asc', 'desc']`
    :   Custom field 111

    `custom112: Literal['asc', 'desc']`
    :   Custom field 112

    `custom113: Literal['asc', 'desc']`
    :   Custom field 113

    `custom114: Literal['asc', 'desc']`
    :   Custom field 114

    `custom115: Literal['asc', 'desc']`
    :   Custom field 115

    `custom116: Literal['asc', 'desc']`
    :   Custom field 116

    `custom117: Literal['asc', 'desc']`
    :   Custom field 117

    `custom118: Literal['asc', 'desc']`
    :   Custom field 118

    `custom119: Literal['asc', 'desc']`
    :   Custom field 119

    `custom12: Literal['asc', 'desc']`
    :   Custom field 12

    `custom120: Literal['asc', 'desc']`
    :   Custom field 120

    `custom121: Literal['asc', 'desc']`
    :   Custom field 121

    `custom122: Literal['asc', 'desc']`
    :   Custom field 122

    `custom123: Literal['asc', 'desc']`
    :   Custom field 123

    `custom124: Literal['asc', 'desc']`
    :   Custom field 124

    `custom125: Literal['asc', 'desc']`
    :   Custom field 125

    `custom126: Literal['asc', 'desc']`
    :   Custom field 126

    `custom127: Literal['asc', 'desc']`
    :   Custom field 127

    `custom128: Literal['asc', 'desc']`
    :   Custom field 128

    `custom129: Literal['asc', 'desc']`
    :   Custom field 129

    `custom13: Literal['asc', 'desc']`
    :   Custom field 13

    `custom130: Literal['asc', 'desc']`
    :   Custom field 130

    `custom131: Literal['asc', 'desc']`
    :   Custom field 131

    `custom132: Literal['asc', 'desc']`
    :   Custom field 132

    `custom133: Literal['asc', 'desc']`
    :   Custom field 133

    `custom134: Literal['asc', 'desc']`
    :   Custom field 134

    `custom135: Literal['asc', 'desc']`
    :   Custom field 135

    `custom136: Literal['asc', 'desc']`
    :   Custom field 136

    `custom137: Literal['asc', 'desc']`
    :   Custom field 137

    `custom138: Literal['asc', 'desc']`
    :   Custom field 138

    `custom139: Literal['asc', 'desc']`
    :   Custom field 139

    `custom14: Literal['asc', 'desc']`
    :   Custom field 14

    `custom140: Literal['asc', 'desc']`
    :   Custom field 140

    `custom141: Literal['asc', 'desc']`
    :   Custom field 141

    `custom142: Literal['asc', 'desc']`
    :   Custom field 142

    `custom143: Literal['asc', 'desc']`
    :   Custom field 143

    `custom144: Literal['asc', 'desc']`
    :   Custom field 144

    `custom145: Literal['asc', 'desc']`
    :   Custom field 145

    `custom146: Literal['asc', 'desc']`
    :   Custom field 146

    `custom147: Literal['asc', 'desc']`
    :   Custom field 147

    `custom148: Literal['asc', 'desc']`
    :   Custom field 148

    `custom149: Literal['asc', 'desc']`
    :   Custom field 149

    `custom15: Literal['asc', 'desc']`
    :   Custom field 15

    `custom150: Literal['asc', 'desc']`
    :   Custom field 150

    `custom16: Literal['asc', 'desc']`
    :   Custom field 16

    `custom17: Literal['asc', 'desc']`
    :   Custom field 17

    `custom18: Literal['asc', 'desc']`
    :   Custom field 18

    `custom19: Literal['asc', 'desc']`
    :   Custom field 19

    `custom2: Literal['asc', 'desc']`
    :   Custom field 2

    `custom20: Literal['asc', 'desc']`
    :   Custom field 20

    `custom21: Literal['asc', 'desc']`
    :   Custom field 21

    `custom22: Literal['asc', 'desc']`
    :   Custom field 22

    `custom23: Literal['asc', 'desc']`
    :   Custom field 23

    `custom24: Literal['asc', 'desc']`
    :   Custom field 24

    `custom25: Literal['asc', 'desc']`
    :   Custom field 25

    `custom26: Literal['asc', 'desc']`
    :   Custom field 26

    `custom27: Literal['asc', 'desc']`
    :   Custom field 27

    `custom28: Literal['asc', 'desc']`
    :   Custom field 28

    `custom29: Literal['asc', 'desc']`
    :   Custom field 29

    `custom3: Literal['asc', 'desc']`
    :   Custom field 3

    `custom30: Literal['asc', 'desc']`
    :   Custom field 30

    `custom31: Literal['asc', 'desc']`
    :   Custom field 31

    `custom32: Literal['asc', 'desc']`
    :   Custom field 32

    `custom33: Literal['asc', 'desc']`
    :   Custom field 33

    `custom34: Literal['asc', 'desc']`
    :   Custom field 34

    `custom35: Literal['asc', 'desc']`
    :   Custom field 35

    `custom36: Literal['asc', 'desc']`
    :   Custom field 36

    `custom37: Literal['asc', 'desc']`
    :   Custom field 37

    `custom38: Literal['asc', 'desc']`
    :   Custom field 38

    `custom39: Literal['asc', 'desc']`
    :   Custom field 39

    `custom4: Literal['asc', 'desc']`
    :   Custom field 4

    `custom40: Literal['asc', 'desc']`
    :   Custom field 40

    `custom41: Literal['asc', 'desc']`
    :   Custom field 41

    `custom42: Literal['asc', 'desc']`
    :   Custom field 42

    `custom43: Literal['asc', 'desc']`
    :   Custom field 43

    `custom44: Literal['asc', 'desc']`
    :   Custom field 44

    `custom45: Literal['asc', 'desc']`
    :   Custom field 45

    `custom46: Literal['asc', 'desc']`
    :   Custom field 46

    `custom47: Literal['asc', 'desc']`
    :   Custom field 47

    `custom48: Literal['asc', 'desc']`
    :   Custom field 48

    `custom49: Literal['asc', 'desc']`
    :   Custom field 49

    `custom5: Literal['asc', 'desc']`
    :   Custom field 5

    `custom50: Literal['asc', 'desc']`
    :   Custom field 50

    `custom51: Literal['asc', 'desc']`
    :   Custom field 51

    `custom52: Literal['asc', 'desc']`
    :   Custom field 52

    `custom53: Literal['asc', 'desc']`
    :   Custom field 53

    `custom54: Literal['asc', 'desc']`
    :   Custom field 54

    `custom55: Literal['asc', 'desc']`
    :   Custom field 55

    `custom56: Literal['asc', 'desc']`
    :   Custom field 56

    `custom57: Literal['asc', 'desc']`
    :   Custom field 57

    `custom58: Literal['asc', 'desc']`
    :   Custom field 58

    `custom59: Literal['asc', 'desc']`
    :   Custom field 59

    `custom6: Literal['asc', 'desc']`
    :   Custom field 6

    `custom60: Literal['asc', 'desc']`
    :   Custom field 60

    `custom61: Literal['asc', 'desc']`
    :   Custom field 61

    `custom62: Literal['asc', 'desc']`
    :   Custom field 62

    `custom63: Literal['asc', 'desc']`
    :   Custom field 63

    `custom64: Literal['asc', 'desc']`
    :   Custom field 64

    `custom65: Literal['asc', 'desc']`
    :   Custom field 65

    `custom66: Literal['asc', 'desc']`
    :   Custom field 66

    `custom67: Literal['asc', 'desc']`
    :   Custom field 67

    `custom68: Literal['asc', 'desc']`
    :   Custom field 68

    `custom69: Literal['asc', 'desc']`
    :   Custom field 69

    `custom7: Literal['asc', 'desc']`
    :   Custom field 7

    `custom70: Literal['asc', 'desc']`
    :   Custom field 70

    `custom71: Literal['asc', 'desc']`
    :   Custom field 71

    `custom72: Literal['asc', 'desc']`
    :   Custom field 72

    `custom73: Literal['asc', 'desc']`
    :   Custom field 73

    `custom74: Literal['asc', 'desc']`
    :   Custom field 74

    `custom75: Literal['asc', 'desc']`
    :   Custom field 75

    `custom76: Literal['asc', 'desc']`
    :   Custom field 76

    `custom77: Literal['asc', 'desc']`
    :   Custom field 77

    `custom78: Literal['asc', 'desc']`
    :   Custom field 78

    `custom79: Literal['asc', 'desc']`
    :   Custom field 79

    `custom8: Literal['asc', 'desc']`
    :   Custom field 8

    `custom80: Literal['asc', 'desc']`
    :   Custom field 80

    `custom81: Literal['asc', 'desc']`
    :   Custom field 81

    `custom82: Literal['asc', 'desc']`
    :   Custom field 82

    `custom83: Literal['asc', 'desc']`
    :   Custom field 83

    `custom84: Literal['asc', 'desc']`
    :   Custom field 84

    `custom85: Literal['asc', 'desc']`
    :   Custom field 85

    `custom86: Literal['asc', 'desc']`
    :   Custom field 86

    `custom87: Literal['asc', 'desc']`
    :   Custom field 87

    `custom88: Literal['asc', 'desc']`
    :   Custom field 88

    `custom89: Literal['asc', 'desc']`
    :   Custom field 89

    `custom9: Literal['asc', 'desc']`
    :   Custom field 9

    `custom90: Literal['asc', 'desc']`
    :   Custom field 90

    `custom91: Literal['asc', 'desc']`
    :   Custom field 91

    `custom92: Literal['asc', 'desc']`
    :   Custom field 92

    `custom93: Literal['asc', 'desc']`
    :   Custom field 93

    `custom94: Literal['asc', 'desc']`
    :   Custom field 94

    `custom95: Literal['asc', 'desc']`
    :   Custom field 95

    `custom96: Literal['asc', 'desc']`
    :   Custom field 96

    `custom97: Literal['asc', 'desc']`
    :   Custom field 97

    `custom98: Literal['asc', 'desc']`
    :   Custom field 98

    `custom99: Literal['asc', 'desc']`
    :   Custom field 99

    `default_plugin_mapping: Literal['asc', 'desc']`
    :   Default plugin mapping

    `description: Literal['asc', 'desc']`
    :   Description

    `external_created_at: Literal['asc', 'desc']`
    :   External created at

    `external_creator: Literal['asc', 'desc']`
    :   External creator

    `favorites: Literal['asc', 'desc']`
    :   Favorites

    `health_category: Literal['asc', 'desc']`
    :   Health category

    `health_score: Literal['asc', 'desc']`
    :   Health score

    `id: Literal['asc', 'desc']`
    :   Unique opportunity identifier

    `map_link: Literal['asc', 'desc']`
    :   Map link

    `map_next_steps: Literal['asc', 'desc']`
    :   Map next steps

    `map_number_of_overdue_tasks: Literal['asc', 'desc']`
    :   Map number of overdue tasks

    `map_status: Literal['asc', 'desc']`
    :   Map status

    `name: Literal['asc', 'desc']`
    :   Name

    `next_step: Literal['asc', 'desc']`
    :   Next step

    `opportunity_health_factors: Literal['asc', 'desc']`
    :   Opportunity health factors

    `opportunity_stage: Literal['asc', 'desc']`
    :   Opportunity stage

    `opportunity_type: Literal['asc', 'desc']`
    :   Opportunity type

    `owner: Literal['asc', 'desc']`
    :   Owner

    `primary_prospect: Literal['asc', 'desc']`
    :   Primary prospect

    `probability: Literal['asc', 'desc']`
    :   Probability

    `prospecting_rep_id: Literal['asc', 'desc']`
    :   Prospecting rep id

    `prospects: Literal['asc', 'desc']`
    :   Prospects

    `sharing_team_id: Literal['asc', 'desc']`
    :   Sharing team id

    `stage: Literal['asc', 'desc']`
    :   Stage

    `tags: Literal['asc', 'desc']`
    :   Tags

    `touched_at: Literal['asc', 'desc']`
    :   Touched at

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

<a id="OpportunitiesStartswithCondition"></a>

`OpportunitiesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.OpportunitiesStringFilter`
    :   The type of the None singleton.

<a id="OpportunitiesStringFilter"></a>

`OpportunitiesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   Account

    `amount: str`
    :   Amount

    `assigned_teams: str`
    :   Assigned teams

    `assigned_users: str`
    :   Assigned users

    `close_date: str`
    :   Close date

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `currency_type: str`
    :   Currency type

    `custom1: str`
    :   Custom field 1

    `custom10: str`
    :   Custom field 10

    `custom100: str`
    :   Custom field 100

    `custom101: str`
    :   Custom field 101

    `custom102: str`
    :   Custom field 102

    `custom103: str`
    :   Custom field 103

    `custom104: str`
    :   Custom field 104

    `custom105: str`
    :   Custom field 105

    `custom106: str`
    :   Custom field 106

    `custom107: str`
    :   Custom field 107

    `custom108: str`
    :   Custom field 108

    `custom109: str`
    :   Custom field 109

    `custom11: str`
    :   Custom field 11

    `custom110: str`
    :   Custom field 110

    `custom111: str`
    :   Custom field 111

    `custom112: str`
    :   Custom field 112

    `custom113: str`
    :   Custom field 113

    `custom114: str`
    :   Custom field 114

    `custom115: str`
    :   Custom field 115

    `custom116: str`
    :   Custom field 116

    `custom117: str`
    :   Custom field 117

    `custom118: str`
    :   Custom field 118

    `custom119: str`
    :   Custom field 119

    `custom12: str`
    :   Custom field 12

    `custom120: str`
    :   Custom field 120

    `custom121: str`
    :   Custom field 121

    `custom122: str`
    :   Custom field 122

    `custom123: str`
    :   Custom field 123

    `custom124: str`
    :   Custom field 124

    `custom125: str`
    :   Custom field 125

    `custom126: str`
    :   Custom field 126

    `custom127: str`
    :   Custom field 127

    `custom128: str`
    :   Custom field 128

    `custom129: str`
    :   Custom field 129

    `custom13: str`
    :   Custom field 13

    `custom130: str`
    :   Custom field 130

    `custom131: str`
    :   Custom field 131

    `custom132: str`
    :   Custom field 132

    `custom133: str`
    :   Custom field 133

    `custom134: str`
    :   Custom field 134

    `custom135: str`
    :   Custom field 135

    `custom136: str`
    :   Custom field 136

    `custom137: str`
    :   Custom field 137

    `custom138: str`
    :   Custom field 138

    `custom139: str`
    :   Custom field 139

    `custom14: str`
    :   Custom field 14

    `custom140: str`
    :   Custom field 140

    `custom141: str`
    :   Custom field 141

    `custom142: str`
    :   Custom field 142

    `custom143: str`
    :   Custom field 143

    `custom144: str`
    :   Custom field 144

    `custom145: str`
    :   Custom field 145

    `custom146: str`
    :   Custom field 146

    `custom147: str`
    :   Custom field 147

    `custom148: str`
    :   Custom field 148

    `custom149: str`
    :   Custom field 149

    `custom15: str`
    :   Custom field 15

    `custom150: str`
    :   Custom field 150

    `custom16: str`
    :   Custom field 16

    `custom17: str`
    :   Custom field 17

    `custom18: str`
    :   Custom field 18

    `custom19: str`
    :   Custom field 19

    `custom2: str`
    :   Custom field 2

    `custom20: str`
    :   Custom field 20

    `custom21: str`
    :   Custom field 21

    `custom22: str`
    :   Custom field 22

    `custom23: str`
    :   Custom field 23

    `custom24: str`
    :   Custom field 24

    `custom25: str`
    :   Custom field 25

    `custom26: str`
    :   Custom field 26

    `custom27: str`
    :   Custom field 27

    `custom28: str`
    :   Custom field 28

    `custom29: str`
    :   Custom field 29

    `custom3: str`
    :   Custom field 3

    `custom30: str`
    :   Custom field 30

    `custom31: str`
    :   Custom field 31

    `custom32: str`
    :   Custom field 32

    `custom33: str`
    :   Custom field 33

    `custom34: str`
    :   Custom field 34

    `custom35: str`
    :   Custom field 35

    `custom36: str`
    :   Custom field 36

    `custom37: str`
    :   Custom field 37

    `custom38: str`
    :   Custom field 38

    `custom39: str`
    :   Custom field 39

    `custom4: str`
    :   Custom field 4

    `custom40: str`
    :   Custom field 40

    `custom41: str`
    :   Custom field 41

    `custom42: str`
    :   Custom field 42

    `custom43: str`
    :   Custom field 43

    `custom44: str`
    :   Custom field 44

    `custom45: str`
    :   Custom field 45

    `custom46: str`
    :   Custom field 46

    `custom47: str`
    :   Custom field 47

    `custom48: str`
    :   Custom field 48

    `custom49: str`
    :   Custom field 49

    `custom5: str`
    :   Custom field 5

    `custom50: str`
    :   Custom field 50

    `custom51: str`
    :   Custom field 51

    `custom52: str`
    :   Custom field 52

    `custom53: str`
    :   Custom field 53

    `custom54: str`
    :   Custom field 54

    `custom55: str`
    :   Custom field 55

    `custom56: str`
    :   Custom field 56

    `custom57: str`
    :   Custom field 57

    `custom58: str`
    :   Custom field 58

    `custom59: str`
    :   Custom field 59

    `custom6: str`
    :   Custom field 6

    `custom60: str`
    :   Custom field 60

    `custom61: str`
    :   Custom field 61

    `custom62: str`
    :   Custom field 62

    `custom63: str`
    :   Custom field 63

    `custom64: str`
    :   Custom field 64

    `custom65: str`
    :   Custom field 65

    `custom66: str`
    :   Custom field 66

    `custom67: str`
    :   Custom field 67

    `custom68: str`
    :   Custom field 68

    `custom69: str`
    :   Custom field 69

    `custom7: str`
    :   Custom field 7

    `custom70: str`
    :   Custom field 70

    `custom71: str`
    :   Custom field 71

    `custom72: str`
    :   Custom field 72

    `custom73: str`
    :   Custom field 73

    `custom74: str`
    :   Custom field 74

    `custom75: str`
    :   Custom field 75

    `custom76: str`
    :   Custom field 76

    `custom77: str`
    :   Custom field 77

    `custom78: str`
    :   Custom field 78

    `custom79: str`
    :   Custom field 79

    `custom8: str`
    :   Custom field 8

    `custom80: str`
    :   Custom field 80

    `custom81: str`
    :   Custom field 81

    `custom82: str`
    :   Custom field 82

    `custom83: str`
    :   Custom field 83

    `custom84: str`
    :   Custom field 84

    `custom85: str`
    :   Custom field 85

    `custom86: str`
    :   Custom field 86

    `custom87: str`
    :   Custom field 87

    `custom88: str`
    :   Custom field 88

    `custom89: str`
    :   Custom field 89

    `custom9: str`
    :   Custom field 9

    `custom90: str`
    :   Custom field 90

    `custom91: str`
    :   Custom field 91

    `custom92: str`
    :   Custom field 92

    `custom93: str`
    :   Custom field 93

    `custom94: str`
    :   Custom field 94

    `custom95: str`
    :   Custom field 95

    `custom96: str`
    :   Custom field 96

    `custom97: str`
    :   Custom field 97

    `custom98: str`
    :   Custom field 98

    `custom99: str`
    :   Custom field 99

    `default_plugin_mapping: str`
    :   Default plugin mapping

    `description: str`
    :   Description

    `external_created_at: str`
    :   External created at

    `external_creator: str`
    :   External creator

    `favorites: str`
    :   Favorites

    `health_category: str`
    :   Health category

    `health_score: str`
    :   Health score

    `id: str`
    :   Unique opportunity identifier

    `map_link: str`
    :   Map link

    `map_next_steps: str`
    :   Map next steps

    `map_number_of_overdue_tasks: str`
    :   Map number of overdue tasks

    `map_status: str`
    :   Map status

    `name: str`
    :   Name

    `next_step: str`
    :   Next step

    `opportunity_health_factors: str`
    :   Opportunity health factors

    `opportunity_stage: str`
    :   Opportunity stage

    `opportunity_type: str`
    :   Opportunity type

    `owner: str`
    :   Owner

    `primary_prospect: str`
    :   Primary prospect

    `probability: str`
    :   Probability

    `prospecting_rep_id: str`
    :   Prospecting rep id

    `prospects: str`
    :   Prospects

    `sharing_team_id: str`
    :   Sharing team id

    `stage: str`
    :   Stage

    `tags: str`
    :   Tags

    `touched_at: str`
    :   Touched at

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

<a id="PersonasAndCondition"></a>

`PersonasAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.PersonasEqCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasNeqCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasGtCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasGteCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasLtCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasLteCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasInCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasContainsCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasNotCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasAndCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasOrCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasAnyCondition]`
    :   The type of the None singleton.

<a id="PersonasAnyCondition"></a>

`PersonasAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.PersonasAnyValueFilter`
    :   The type of the None singleton.

<a id="PersonasAnyValueFilter"></a>

`PersonasAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Created at

    `description: Any`
    :   Description

    `id: Any`
    :   Unique persona identifier

    `name: Any`
    :   Name

    `prospects: Any`
    :   Prospects

    `updated_at: Any`
    :   Updated at

<a id="PersonasArrayContainsCondition"></a>

`PersonasArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.PersonasAnyValueFilter`
    :   The type of the None singleton.

<a id="PersonasContainsCondition"></a>

`PersonasContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.PersonasAnyValueFilter`
    :   The type of the None singleton.

<a id="PersonasEndswithCondition"></a>

`PersonasEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.PersonasStringFilter`
    :   The type of the None singleton.

<a id="PersonasEqCondition"></a>

`PersonasEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.PersonasSearchFilter`
    :   The type of the None singleton.

<a id="PersonasFuzzyCondition"></a>

`PersonasFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.PersonasStringFilter`
    :   The type of the None singleton.

<a id="PersonasGetParams"></a>

`PersonasGetParams(*args, **kwargs)`
:   Parameters for personas.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PersonasGtCondition"></a>

`PersonasGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.PersonasSearchFilter`
    :   The type of the None singleton.

<a id="PersonasGteCondition"></a>

`PersonasGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.PersonasSearchFilter`
    :   The type of the None singleton.

<a id="PersonasInCondition"></a>

`PersonasInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.PersonasInFilter`
    :   The type of the None singleton.

<a id="PersonasInFilter"></a>

`PersonasInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Created at

    `description: list[str]`
    :   Description

    `id: list[int]`
    :   Unique persona identifier

    `name: list[str]`
    :   Name

    `prospects: list[list[typing.Any]]`
    :   Prospects

    `updated_at: list[str]`
    :   Updated at

<a id="PersonasKeywordCondition"></a>

`PersonasKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.PersonasStringFilter`
    :   The type of the None singleton.

<a id="PersonasListParams"></a>

`PersonasListParams(*args, **kwargs)`
:   Parameters for personas.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="PersonasLtCondition"></a>

`PersonasLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.PersonasSearchFilter`
    :   The type of the None singleton.

<a id="PersonasLteCondition"></a>

`PersonasLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.PersonasSearchFilter`
    :   The type of the None singleton.

<a id="PersonasNeqCondition"></a>

`PersonasNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.PersonasSearchFilter`
    :   The type of the None singleton.

<a id="PersonasNotCondition"></a>

`PersonasNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.PersonasEqCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasNeqCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasGtCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasGteCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasLtCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasLteCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasInCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasContainsCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasNotCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasAndCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasOrCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasAnyCondition`
    :   The type of the None singleton.

<a id="PersonasOrCondition"></a>

`PersonasOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.PersonasEqCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasNeqCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasGtCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasGteCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasLtCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasLteCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasInCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasContainsCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasNotCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasAndCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasOrCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasAnyCondition]`
    :   The type of the None singleton.

<a id="PersonasSearchFilter"></a>

`PersonasSearchFilter(*args, **kwargs)`
:   Available fields for filtering personas search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Created at

    `description: str | None`
    :   Description

    `id: int | None`
    :   Unique persona identifier

    `name: str | None`
    :   Name

    `prospects: list[typing.Any] | None`
    :   Prospects

    `updated_at: str | None`
    :   Updated at

<a id="PersonasSearchQuery"></a>

`PersonasSearchQuery(*args, **kwargs)`
:   Search query for personas entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.PersonasEqCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasNeqCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasGtCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasGteCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasLtCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasLteCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasInCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasContainsCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasNotCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasAndCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasOrCondition | airbyte_agent_sdk.connectors.outreach.types.PersonasAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.PersonasSortFilter]`
    :   The type of the None singleton.

<a id="PersonasSortFilter"></a>

`PersonasSortFilter(*args, **kwargs)`
:   Available fields for sorting personas search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `description: Literal['asc', 'desc']`
    :   Description

    `id: Literal['asc', 'desc']`
    :   Unique persona identifier

    `name: Literal['asc', 'desc']`
    :   Name

    `prospects: Literal['asc', 'desc']`
    :   Prospects

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

<a id="PersonasStartswithCondition"></a>

`PersonasStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.PersonasStringFilter`
    :   The type of the None singleton.

<a id="PersonasStringFilter"></a>

`PersonasStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Created at

    `description: str`
    :   Description

    `id: str`
    :   Unique persona identifier

    `name: str`
    :   Name

    `prospects: str`
    :   Prospects

    `updated_at: str`
    :   Updated at

<a id="ProspectsAndCondition"></a>

`ProspectsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.ProspectsEqCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsGtCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsGteCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsLtCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsLteCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsInCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsNotCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsAndCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsOrCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProspectsAnyCondition"></a>

`ProspectsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.ProspectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProspectsAnyValueFilter"></a>

`ProspectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Any`
    :   Account

    `account_name: Any`
    :   Account name

    `active_sequence_states: Any`
    :   Active sequence states

    `added_at: Any`
    :   Added at

    `address_city: Any`
    :   Address city

    `address_country: Any`
    :   Address country

    `address_state: Any`
    :   Address state

    `address_street: Any`
    :   Address street

    `address_street2: Any`
    :   Address street2

    `address_zip: Any`
    :   Address zip

    `angel_list_url: Any`
    :   Angel list url

    `assigned_teams: Any`
    :   Assigned teams

    `assigned_users: Any`
    :   Assigned users

    `available_at: Any`
    :   Available at

    `batches: Any`
    :   Batches

    `call_opted_out: Any`
    :   Call opted out

    `calls: Any`
    :   Calls

    `calls_opt_status: Any`
    :   Calls opt status

    `calls_opted_at: Any`
    :   Calls opted at

    `campaign_name: Any`
    :   Campaign name

    `click_count: Any`
    :   Click count

    `company: Any`
    :   Company

    `company_followers: Any`
    :   Company followers

    `company_founded_at: Any`
    :   Company founded at

    `company_industry: Any`
    :   Company industry

    `company_linked_in: Any`
    :   Company linked in

    `company_linked_in_employees: Any`
    :   Company linked in employees

    `company_locality: Any`
    :   Company locality

    `company_natural: Any`
    :   Company natural

    `company_size: Any`
    :   Company size

    `company_start_date: Any`
    :   Company start date

    `company_type: Any`
    :   Company type

    `contact_histogram: Any`
    :   Contact histogram

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `custom1: Any`
    :   Custom field 1

    `custom10: Any`
    :   Custom field 10

    `custom100: Any`
    :   Custom field 100

    `custom101: Any`
    :   Custom field 101

    `custom102: Any`
    :   Custom field 102

    `custom103: Any`
    :   Custom field 103

    `custom104: Any`
    :   Custom field 104

    `custom105: Any`
    :   Custom field 105

    `custom106: Any`
    :   Custom field 106

    `custom107: Any`
    :   Custom field 107

    `custom108: Any`
    :   Custom field 108

    `custom109: Any`
    :   Custom field 109

    `custom11: Any`
    :   Custom field 11

    `custom110: Any`
    :   Custom field 110

    `custom111: Any`
    :   Custom field 111

    `custom112: Any`
    :   Custom field 112

    `custom113: Any`
    :   Custom field 113

    `custom114: Any`
    :   Custom field 114

    `custom115: Any`
    :   Custom field 115

    `custom116: Any`
    :   Custom field 116

    `custom117: Any`
    :   Custom field 117

    `custom118: Any`
    :   Custom field 118

    `custom119: Any`
    :   Custom field 119

    `custom12: Any`
    :   Custom field 12

    `custom120: Any`
    :   Custom field 120

    `custom121: Any`
    :   Custom field 121

    `custom122: Any`
    :   Custom field 122

    `custom123: Any`
    :   Custom field 123

    `custom124: Any`
    :   Custom field 124

    `custom125: Any`
    :   Custom field 125

    `custom126: Any`
    :   Custom field 126

    `custom127: Any`
    :   Custom field 127

    `custom128: Any`
    :   Custom field 128

    `custom129: Any`
    :   Custom field 129

    `custom13: Any`
    :   Custom field 13

    `custom130: Any`
    :   Custom field 130

    `custom131: Any`
    :   Custom field 131

    `custom132: Any`
    :   Custom field 132

    `custom133: Any`
    :   Custom field 133

    `custom134: Any`
    :   Custom field 134

    `custom135: Any`
    :   Custom field 135

    `custom136: Any`
    :   Custom field 136

    `custom137: Any`
    :   Custom field 137

    `custom138: Any`
    :   Custom field 138

    `custom139: Any`
    :   Custom field 139

    `custom14: Any`
    :   Custom field 14

    `custom140: Any`
    :   Custom field 140

    `custom141: Any`
    :   Custom field 141

    `custom142: Any`
    :   Custom field 142

    `custom143: Any`
    :   Custom field 143

    `custom144: Any`
    :   Custom field 144

    `custom145: Any`
    :   Custom field 145

    `custom146: Any`
    :   Custom field 146

    `custom147: Any`
    :   Custom field 147

    `custom148: Any`
    :   Custom field 148

    `custom149: Any`
    :   Custom field 149

    `custom15: Any`
    :   Custom field 15

    `custom150: Any`
    :   Custom field 150

    `custom16: Any`
    :   Custom field 16

    `custom17: Any`
    :   Custom field 17

    `custom18: Any`
    :   Custom field 18

    `custom19: Any`
    :   Custom field 19

    `custom2: Any`
    :   Custom field 2

    `custom20: Any`
    :   Custom field 20

    `custom21: Any`
    :   Custom field 21

    `custom22: Any`
    :   Custom field 22

    `custom23: Any`
    :   Custom field 23

    `custom24: Any`
    :   Custom field 24

    `custom25: Any`
    :   Custom field 25

    `custom26: Any`
    :   Custom field 26

    `custom27: Any`
    :   Custom field 27

    `custom28: Any`
    :   Custom field 28

    `custom29: Any`
    :   Custom field 29

    `custom3: Any`
    :   Custom field 3

    `custom30: Any`
    :   Custom field 30

    `custom31: Any`
    :   Custom field 31

    `custom32: Any`
    :   Custom field 32

    `custom33: Any`
    :   Custom field 33

    `custom34: Any`
    :   Custom field 34

    `custom35: Any`
    :   Custom field 35

    `custom36: Any`
    :   Custom field 36

    `custom37: Any`
    :   Custom field 37

    `custom38: Any`
    :   Custom field 38

    `custom39: Any`
    :   Custom field 39

    `custom4: Any`
    :   Custom field 4

    `custom40: Any`
    :   Custom field 40

    `custom41: Any`
    :   Custom field 41

    `custom42: Any`
    :   Custom field 42

    `custom43: Any`
    :   Custom field 43

    `custom44: Any`
    :   Custom field 44

    `custom45: Any`
    :   Custom field 45

    `custom46: Any`
    :   Custom field 46

    `custom47: Any`
    :   Custom field 47

    `custom48: Any`
    :   Custom field 48

    `custom49: Any`
    :   Custom field 49

    `custom5: Any`
    :   Custom field 5

    `custom50: Any`
    :   Custom field 50

    `custom51: Any`
    :   Custom field 51

    `custom52: Any`
    :   Custom field 52

    `custom53: Any`
    :   Custom field 53

    `custom54: Any`
    :   Custom field 54

    `custom55: Any`
    :   Custom field 55

    `custom56: Any`
    :   Custom field 56

    `custom57: Any`
    :   Custom field 57

    `custom58: Any`
    :   Custom field 58

    `custom59: Any`
    :   Custom field 59

    `custom6: Any`
    :   Custom field 6

    `custom60: Any`
    :   Custom field 60

    `custom61: Any`
    :   Custom field 61

    `custom62: Any`
    :   Custom field 62

    `custom63: Any`
    :   Custom field 63

    `custom64: Any`
    :   Custom field 64

    `custom65: Any`
    :   Custom field 65

    `custom66: Any`
    :   Custom field 66

    `custom67: Any`
    :   Custom field 67

    `custom68: Any`
    :   Custom field 68

    `custom69: Any`
    :   Custom field 69

    `custom7: Any`
    :   Custom field 7

    `custom70: Any`
    :   Custom field 70

    `custom71: Any`
    :   Custom field 71

    `custom72: Any`
    :   Custom field 72

    `custom73: Any`
    :   Custom field 73

    `custom74: Any`
    :   Custom field 74

    `custom75: Any`
    :   Custom field 75

    `custom76: Any`
    :   Custom field 76

    `custom77: Any`
    :   Custom field 77

    `custom78: Any`
    :   Custom field 78

    `custom79: Any`
    :   Custom field 79

    `custom8: Any`
    :   Custom field 8

    `custom80: Any`
    :   Custom field 80

    `custom81: Any`
    :   Custom field 81

    `custom82: Any`
    :   Custom field 82

    `custom83: Any`
    :   Custom field 83

    `custom84: Any`
    :   Custom field 84

    `custom85: Any`
    :   Custom field 85

    `custom86: Any`
    :   Custom field 86

    `custom87: Any`
    :   Custom field 87

    `custom88: Any`
    :   Custom field 88

    `custom89: Any`
    :   Custom field 89

    `custom9: Any`
    :   Custom field 9

    `custom90: Any`
    :   Custom field 90

    `custom91: Any`
    :   Custom field 91

    `custom92: Any`
    :   Custom field 92

    `custom93: Any`
    :   Custom field 93

    `custom94: Any`
    :   Custom field 94

    `custom95: Any`
    :   Custom field 95

    `custom96: Any`
    :   Custom field 96

    `custom97: Any`
    :   Custom field 97

    `custom98: Any`
    :   Custom field 98

    `custom99: Any`
    :   Custom field 99

    `date_of_birth: Any`
    :   Date of birth

    `default_plugin_mapping: Any`
    :   Default plugin mapping

    `degree: Any`
    :   Degree

    `email_addresses: Any`
    :   Email addresses

    `email_contacts: Any`
    :   Email contacts

    `email_opted_out: Any`
    :   Email opted out

    `emails: Any`
    :   Emails

    `emails_opt_status: Any`
    :   Emails opt status

    `emails_opted_at: Any`
    :   Emails opted at

    `engaged_at: Any`
    :   Engaged at

    `engaged_score: Any`
    :   Engaged score

    `event_name: Any`
    :   Event name

    `external_id: Any`
    :   External id

    `external_owner: Any`
    :   External owner

    `external_source: Any`
    :   External source

    `facebook_url: Any`
    :   Facebook url

    `favorites: Any`
    :   Favorites

    `first_name: Any`
    :   First name

    `gender: Any`
    :   Gender

    `github_url: Any`
    :   Github url

    `github_username: Any`
    :   Github username

    `google_plus_url: Any`
    :   Google plus url

    `graduation_date: Any`
    :   Graduation date

    `home_phones: Any`
    :   Home phones

    `id: Any`
    :   Unique prospect identifier

    `job_start_date: Any`
    :   Job start date

    `last_name: Any`
    :   Last name

    `linked_in_connections: Any`
    :   Linked in connections

    `linked_in_id: Any`
    :   Linked in id

    `linked_in_slug: Any`
    :   Linked in slug

    `linked_in_url: Any`
    :   Linked in url

    `mailings: Any`
    :   Mailings

    `middle_name: Any`
    :   Middle name

    `mobile_phones: Any`
    :   Mobile phones

    `name: Any`
    :   Name

    `nickname: Any`
    :   Nickname

    `occupation: Any`
    :   Occupation

    `open_count: Any`
    :   Open count

    `opportunities: Any`
    :   Opportunities

    `opportunity_prospect_roles: Any`
    :   Opportunity prospect roles

    `opted_out: Any`
    :   Opted out

    `opted_out_at: Any`
    :   Opted out at

    `other_phones: Any`
    :   Other phones

    `owner: Any`
    :   Owner

    `persona: Any`
    :   Persona

    `persona_name: Any`
    :   Persona name

    `personal_note1: Any`
    :   Personal note1

    `personal_note2: Any`
    :   Personal note2

    `phone_numbers: Any`
    :   Phone numbers

    `preferred_contact: Any`
    :   Preferred contact

    `quora_url: Any`
    :   Quora url

    `region: Any`
    :   Region

    `reply_count: Any`
    :   Reply count

    `school: Any`
    :   School

    `score: Any`
    :   Score

    `sequence_states: Any`
    :   Sequence states

    `sharing_team_id: Any`
    :   Sharing team id

    `sms_opt_status: Any`
    :   Sms opt status

    `sms_opted_at: Any`
    :   Sms opted at

    `sms_opted_out: Any`
    :   Sms opted out

    `source: Any`
    :   Source

    `specialties: Any`
    :   Specialties

    `stack_overflow_id: Any`
    :   Stack overflow id

    `stack_overflow_url: Any`
    :   Stack overflow url

    `stage: Any`
    :   Stage

    `stage_name: Any`
    :   Stage name

    `tags: Any`
    :   Tags

    `tasks: Any`
    :   Tasks

    `time_zone: Any`
    :   Time zone

    `time_zone_iana: Any`
    :   Time zone iana

    `time_zone_inferred: Any`
    :   Time zone inferred

    `title: Any`
    :   Title

    `touched_at: Any`
    :   Touched at

    `trashed_at: Any`
    :   Trashed at

    `trashed_by_account: Any`
    :   Trashed by account

    `twitter_url: Any`
    :   Twitter url

    `twitter_username: Any`
    :   Twitter username

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

    `updater_id: Any`
    :   Updater id

    `updater_type: Any`
    :   Updater type

    `voip_phones: Any`
    :   Voip phones

    `website_url1: Any`
    :   Website url1

    `website_url2: Any`
    :   Website url2

    `website_url3: Any`
    :   Website url3

    `work_phones: Any`
    :   Work phones

<a id="ProspectsArrayContainsCondition"></a>

`ProspectsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.ProspectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProspectsContainsCondition"></a>

`ProspectsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.ProspectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProspectsEndswithCondition"></a>

`ProspectsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.ProspectsStringFilter`
    :   The type of the None singleton.

<a id="ProspectsEqCondition"></a>

`ProspectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.ProspectsSearchFilter`
    :   The type of the None singleton.

<a id="ProspectsFuzzyCondition"></a>

`ProspectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.ProspectsStringFilter`
    :   The type of the None singleton.

<a id="ProspectsGetParams"></a>

`ProspectsGetParams(*args, **kwargs)`
:   Parameters for prospects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProspectsGtCondition"></a>

`ProspectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.ProspectsSearchFilter`
    :   The type of the None singleton.

<a id="ProspectsGteCondition"></a>

`ProspectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.ProspectsSearchFilter`
    :   The type of the None singleton.

<a id="ProspectsInCondition"></a>

`ProspectsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.ProspectsInFilter`
    :   The type of the None singleton.

<a id="ProspectsInFilter"></a>

`ProspectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: list[list[typing.Any]]`
    :   Account

    `account_name: list[str]`
    :   Account name

    `active_sequence_states: list[list[typing.Any]]`
    :   Active sequence states

    `added_at: list[str]`
    :   Added at

    `address_city: list[str]`
    :   Address city

    `address_country: list[str]`
    :   Address country

    `address_state: list[str]`
    :   Address state

    `address_street: list[str]`
    :   Address street

    `address_street2: list[str]`
    :   Address street2

    `address_zip: list[str]`
    :   Address zip

    `angel_list_url: list[str]`
    :   Angel list url

    `assigned_teams: list[list[typing.Any]]`
    :   Assigned teams

    `assigned_users: list[list[typing.Any]]`
    :   Assigned users

    `available_at: list[str]`
    :   Available at

    `batches: list[list[typing.Any]]`
    :   Batches

    `call_opted_out: list[bool]`
    :   Call opted out

    `calls: list[list[typing.Any]]`
    :   Calls

    `calls_opt_status: list[str]`
    :   Calls opt status

    `calls_opted_at: list[str]`
    :   Calls opted at

    `campaign_name: list[str]`
    :   Campaign name

    `click_count: list[int]`
    :   Click count

    `company: list[str]`
    :   Company

    `company_followers: list[int]`
    :   Company followers

    `company_founded_at: list[str]`
    :   Company founded at

    `company_industry: list[str]`
    :   Company industry

    `company_linked_in: list[str]`
    :   Company linked in

    `company_linked_in_employees: list[str]`
    :   Company linked in employees

    `company_locality: list[str]`
    :   Company locality

    `company_natural: list[str]`
    :   Company natural

    `company_size: list[int]`
    :   Company size

    `company_start_date: list[str]`
    :   Company start date

    `company_type: list[str]`
    :   Company type

    `contact_histogram: list[list[typing.Any]]`
    :   Contact histogram

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `custom1: list[str]`
    :   Custom field 1

    `custom10: list[str]`
    :   Custom field 10

    `custom100: list[str]`
    :   Custom field 100

    `custom101: list[str]`
    :   Custom field 101

    `custom102: list[str]`
    :   Custom field 102

    `custom103: list[str]`
    :   Custom field 103

    `custom104: list[str]`
    :   Custom field 104

    `custom105: list[str]`
    :   Custom field 105

    `custom106: list[str]`
    :   Custom field 106

    `custom107: list[str]`
    :   Custom field 107

    `custom108: list[str]`
    :   Custom field 108

    `custom109: list[str]`
    :   Custom field 109

    `custom11: list[str]`
    :   Custom field 11

    `custom110: list[str]`
    :   Custom field 110

    `custom111: list[str]`
    :   Custom field 111

    `custom112: list[str]`
    :   Custom field 112

    `custom113: list[str]`
    :   Custom field 113

    `custom114: list[str]`
    :   Custom field 114

    `custom115: list[str]`
    :   Custom field 115

    `custom116: list[str]`
    :   Custom field 116

    `custom117: list[str]`
    :   Custom field 117

    `custom118: list[str]`
    :   Custom field 118

    `custom119: list[str]`
    :   Custom field 119

    `custom12: list[str]`
    :   Custom field 12

    `custom120: list[str]`
    :   Custom field 120

    `custom121: list[str]`
    :   Custom field 121

    `custom122: list[str]`
    :   Custom field 122

    `custom123: list[str]`
    :   Custom field 123

    `custom124: list[str]`
    :   Custom field 124

    `custom125: list[str]`
    :   Custom field 125

    `custom126: list[str]`
    :   Custom field 126

    `custom127: list[str]`
    :   Custom field 127

    `custom128: list[str]`
    :   Custom field 128

    `custom129: list[str]`
    :   Custom field 129

    `custom13: list[str]`
    :   Custom field 13

    `custom130: list[str]`
    :   Custom field 130

    `custom131: list[str]`
    :   Custom field 131

    `custom132: list[str]`
    :   Custom field 132

    `custom133: list[str]`
    :   Custom field 133

    `custom134: list[str]`
    :   Custom field 134

    `custom135: list[str]`
    :   Custom field 135

    `custom136: list[str]`
    :   Custom field 136

    `custom137: list[str]`
    :   Custom field 137

    `custom138: list[str]`
    :   Custom field 138

    `custom139: list[str]`
    :   Custom field 139

    `custom14: list[str]`
    :   Custom field 14

    `custom140: list[str]`
    :   Custom field 140

    `custom141: list[str]`
    :   Custom field 141

    `custom142: list[str]`
    :   Custom field 142

    `custom143: list[str]`
    :   Custom field 143

    `custom144: list[str]`
    :   Custom field 144

    `custom145: list[str]`
    :   Custom field 145

    `custom146: list[str]`
    :   Custom field 146

    `custom147: list[str]`
    :   Custom field 147

    `custom148: list[str]`
    :   Custom field 148

    `custom149: list[str]`
    :   Custom field 149

    `custom15: list[str]`
    :   Custom field 15

    `custom150: list[str]`
    :   Custom field 150

    `custom16: list[str]`
    :   Custom field 16

    `custom17: list[str]`
    :   Custom field 17

    `custom18: list[str]`
    :   Custom field 18

    `custom19: list[str]`
    :   Custom field 19

    `custom2: list[str]`
    :   Custom field 2

    `custom20: list[str]`
    :   Custom field 20

    `custom21: list[str]`
    :   Custom field 21

    `custom22: list[str]`
    :   Custom field 22

    `custom23: list[str]`
    :   Custom field 23

    `custom24: list[str]`
    :   Custom field 24

    `custom25: list[str]`
    :   Custom field 25

    `custom26: list[str]`
    :   Custom field 26

    `custom27: list[str]`
    :   Custom field 27

    `custom28: list[str]`
    :   Custom field 28

    `custom29: list[str]`
    :   Custom field 29

    `custom3: list[str]`
    :   Custom field 3

    `custom30: list[str]`
    :   Custom field 30

    `custom31: list[str]`
    :   Custom field 31

    `custom32: list[str]`
    :   Custom field 32

    `custom33: list[str]`
    :   Custom field 33

    `custom34: list[str]`
    :   Custom field 34

    `custom35: list[str]`
    :   Custom field 35

    `custom36: list[str]`
    :   Custom field 36

    `custom37: list[str]`
    :   Custom field 37

    `custom38: list[str]`
    :   Custom field 38

    `custom39: list[str]`
    :   Custom field 39

    `custom4: list[str]`
    :   Custom field 4

    `custom40: list[str]`
    :   Custom field 40

    `custom41: list[str]`
    :   Custom field 41

    `custom42: list[str]`
    :   Custom field 42

    `custom43: list[str]`
    :   Custom field 43

    `custom44: list[str]`
    :   Custom field 44

    `custom45: list[str]`
    :   Custom field 45

    `custom46: list[str]`
    :   Custom field 46

    `custom47: list[str]`
    :   Custom field 47

    `custom48: list[str]`
    :   Custom field 48

    `custom49: list[str]`
    :   Custom field 49

    `custom5: list[str]`
    :   Custom field 5

    `custom50: list[str]`
    :   Custom field 50

    `custom51: list[str]`
    :   Custom field 51

    `custom52: list[str]`
    :   Custom field 52

    `custom53: list[str]`
    :   Custom field 53

    `custom54: list[str]`
    :   Custom field 54

    `custom55: list[str]`
    :   Custom field 55

    `custom56: list[str]`
    :   Custom field 56

    `custom57: list[str]`
    :   Custom field 57

    `custom58: list[str]`
    :   Custom field 58

    `custom59: list[str]`
    :   Custom field 59

    `custom6: list[str]`
    :   Custom field 6

    `custom60: list[str]`
    :   Custom field 60

    `custom61: list[str]`
    :   Custom field 61

    `custom62: list[str]`
    :   Custom field 62

    `custom63: list[str]`
    :   Custom field 63

    `custom64: list[str]`
    :   Custom field 64

    `custom65: list[str]`
    :   Custom field 65

    `custom66: list[str]`
    :   Custom field 66

    `custom67: list[str]`
    :   Custom field 67

    `custom68: list[str]`
    :   Custom field 68

    `custom69: list[str]`
    :   Custom field 69

    `custom7: list[str]`
    :   Custom field 7

    `custom70: list[str]`
    :   Custom field 70

    `custom71: list[str]`
    :   Custom field 71

    `custom72: list[str]`
    :   Custom field 72

    `custom73: list[str]`
    :   Custom field 73

    `custom74: list[str]`
    :   Custom field 74

    `custom75: list[str]`
    :   Custom field 75

    `custom76: list[str]`
    :   Custom field 76

    `custom77: list[str]`
    :   Custom field 77

    `custom78: list[str]`
    :   Custom field 78

    `custom79: list[str]`
    :   Custom field 79

    `custom8: list[str]`
    :   Custom field 8

    `custom80: list[str]`
    :   Custom field 80

    `custom81: list[str]`
    :   Custom field 81

    `custom82: list[str]`
    :   Custom field 82

    `custom83: list[str]`
    :   Custom field 83

    `custom84: list[str]`
    :   Custom field 84

    `custom85: list[str]`
    :   Custom field 85

    `custom86: list[str]`
    :   Custom field 86

    `custom87: list[str]`
    :   Custom field 87

    `custom88: list[str]`
    :   Custom field 88

    `custom89: list[str]`
    :   Custom field 89

    `custom9: list[str]`
    :   Custom field 9

    `custom90: list[str]`
    :   Custom field 90

    `custom91: list[str]`
    :   Custom field 91

    `custom92: list[str]`
    :   Custom field 92

    `custom93: list[str]`
    :   Custom field 93

    `custom94: list[str]`
    :   Custom field 94

    `custom95: list[str]`
    :   Custom field 95

    `custom96: list[str]`
    :   Custom field 96

    `custom97: list[str]`
    :   Custom field 97

    `custom98: list[str]`
    :   Custom field 98

    `custom99: list[str]`
    :   Custom field 99

    `date_of_birth: list[str]`
    :   Date of birth

    `default_plugin_mapping: list[list[typing.Any]]`
    :   Default plugin mapping

    `degree: list[str]`
    :   Degree

    `email_addresses: list[list[typing.Any]]`
    :   Email addresses

    `email_contacts: list[list[typing.Any]]`
    :   Email contacts

    `email_opted_out: list[bool]`
    :   Email opted out

    `emails: list[list[typing.Any]]`
    :   Emails

    `emails_opt_status: list[str]`
    :   Emails opt status

    `emails_opted_at: list[str]`
    :   Emails opted at

    `engaged_at: list[str]`
    :   Engaged at

    `engaged_score: list[float]`
    :   Engaged score

    `event_name: list[str]`
    :   Event name

    `external_id: list[str]`
    :   External id

    `external_owner: list[str]`
    :   External owner

    `external_source: list[str]`
    :   External source

    `facebook_url: list[str]`
    :   Facebook url

    `favorites: list[list[typing.Any]]`
    :   Favorites

    `first_name: list[str]`
    :   First name

    `gender: list[str]`
    :   Gender

    `github_url: list[str]`
    :   Github url

    `github_username: list[str]`
    :   Github username

    `google_plus_url: list[str]`
    :   Google plus url

    `graduation_date: list[str]`
    :   Graduation date

    `home_phones: list[list[typing.Any]]`
    :   Home phones

    `id: list[int]`
    :   Unique prospect identifier

    `job_start_date: list[str]`
    :   Job start date

    `last_name: list[str]`
    :   Last name

    `linked_in_connections: list[int]`
    :   Linked in connections

    `linked_in_id: list[str]`
    :   Linked in id

    `linked_in_slug: list[str]`
    :   Linked in slug

    `linked_in_url: list[str]`
    :   Linked in url

    `mailings: list[list[typing.Any]]`
    :   Mailings

    `middle_name: list[str]`
    :   Middle name

    `mobile_phones: list[list[typing.Any]]`
    :   Mobile phones

    `name: list[str]`
    :   Name

    `nickname: list[str]`
    :   Nickname

    `occupation: list[str]`
    :   Occupation

    `open_count: list[int]`
    :   Open count

    `opportunities: list[list[typing.Any]]`
    :   Opportunities

    `opportunity_prospect_roles: list[list[typing.Any]]`
    :   Opportunity prospect roles

    `opted_out: list[bool]`
    :   Opted out

    `opted_out_at: list[str]`
    :   Opted out at

    `other_phones: list[list[typing.Any]]`
    :   Other phones

    `owner: list[list[typing.Any]]`
    :   Owner

    `persona: list[list[typing.Any]]`
    :   Persona

    `persona_name: list[str]`
    :   Persona name

    `personal_note1: list[str]`
    :   Personal note1

    `personal_note2: list[str]`
    :   Personal note2

    `phone_numbers: list[list[typing.Any]]`
    :   Phone numbers

    `preferred_contact: list[str]`
    :   Preferred contact

    `quora_url: list[str]`
    :   Quora url

    `region: list[str]`
    :   Region

    `reply_count: list[int]`
    :   Reply count

    `school: list[str]`
    :   School

    `score: list[float]`
    :   Score

    `sequence_states: list[list[typing.Any]]`
    :   Sequence states

    `sharing_team_id: list[str]`
    :   Sharing team id

    `sms_opt_status: list[str]`
    :   Sms opt status

    `sms_opted_at: list[str]`
    :   Sms opted at

    `sms_opted_out: list[bool]`
    :   Sms opted out

    `source: list[str]`
    :   Source

    `specialties: list[str]`
    :   Specialties

    `stack_overflow_id: list[str]`
    :   Stack overflow id

    `stack_overflow_url: list[str]`
    :   Stack overflow url

    `stage: list[list[typing.Any]]`
    :   Stage

    `stage_name: list[str]`
    :   Stage name

    `tags: list[list[typing.Any]]`
    :   Tags

    `tasks: list[list[typing.Any]]`
    :   Tasks

    `time_zone: list[str]`
    :   Time zone

    `time_zone_iana: list[str]`
    :   Time zone iana

    `time_zone_inferred: list[str]`
    :   Time zone inferred

    `title: list[str]`
    :   Title

    `touched_at: list[str]`
    :   Touched at

    `trashed_at: list[str]`
    :   Trashed at

    `trashed_by_account: list[list[typing.Any]]`
    :   Trashed by account

    `twitter_url: list[str]`
    :   Twitter url

    `twitter_username: list[str]`
    :   Twitter username

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

    `updater_id: list[int]`
    :   Updater id

    `updater_type: list[str]`
    :   Updater type

    `voip_phones: list[list[typing.Any]]`
    :   Voip phones

    `website_url1: list[str]`
    :   Website url1

    `website_url2: list[str]`
    :   Website url2

    `website_url3: list[str]`
    :   Website url3

    `work_phones: list[list[typing.Any]]`
    :   Work phones

<a id="ProspectsKeywordCondition"></a>

`ProspectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.ProspectsStringFilter`
    :   The type of the None singleton.

<a id="ProspectsListParams"></a>

`ProspectsListParams(*args, **kwargs)`
:   Parameters for prospects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="ProspectsLtCondition"></a>

`ProspectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.ProspectsSearchFilter`
    :   The type of the None singleton.

<a id="ProspectsLteCondition"></a>

`ProspectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.ProspectsSearchFilter`
    :   The type of the None singleton.

<a id="ProspectsNeqCondition"></a>

`ProspectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.ProspectsSearchFilter`
    :   The type of the None singleton.

<a id="ProspectsNotCondition"></a>

`ProspectsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.ProspectsEqCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsGtCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsGteCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsLtCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsLteCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsInCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsNotCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsAndCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsOrCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsAnyCondition`
    :   The type of the None singleton.

<a id="ProspectsOrCondition"></a>

`ProspectsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.ProspectsEqCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsGtCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsGteCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsLtCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsLteCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsInCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsNotCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsAndCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsOrCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProspectsSearchFilter"></a>

`ProspectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering prospects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ProspectsSearchQuery"></a>

`ProspectsSearchQuery(*args, **kwargs)`
:   Search query for prospects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.ProspectsEqCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsGtCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsGteCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsLtCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsLteCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsInCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsNotCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsAndCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsOrCondition | airbyte_agent_sdk.connectors.outreach.types.ProspectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.ProspectsSortFilter]`
    :   The type of the None singleton.

<a id="ProspectsSortFilter"></a>

`ProspectsSortFilter(*args, **kwargs)`
:   Available fields for sorting prospects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Literal['asc', 'desc']`
    :   Account

    `account_name: Literal['asc', 'desc']`
    :   Account name

    `active_sequence_states: Literal['asc', 'desc']`
    :   Active sequence states

    `added_at: Literal['asc', 'desc']`
    :   Added at

    `address_city: Literal['asc', 'desc']`
    :   Address city

    `address_country: Literal['asc', 'desc']`
    :   Address country

    `address_state: Literal['asc', 'desc']`
    :   Address state

    `address_street: Literal['asc', 'desc']`
    :   Address street

    `address_street2: Literal['asc', 'desc']`
    :   Address street2

    `address_zip: Literal['asc', 'desc']`
    :   Address zip

    `angel_list_url: Literal['asc', 'desc']`
    :   Angel list url

    `assigned_teams: Literal['asc', 'desc']`
    :   Assigned teams

    `assigned_users: Literal['asc', 'desc']`
    :   Assigned users

    `available_at: Literal['asc', 'desc']`
    :   Available at

    `batches: Literal['asc', 'desc']`
    :   Batches

    `call_opted_out: Literal['asc', 'desc']`
    :   Call opted out

    `calls: Literal['asc', 'desc']`
    :   Calls

    `calls_opt_status: Literal['asc', 'desc']`
    :   Calls opt status

    `calls_opted_at: Literal['asc', 'desc']`
    :   Calls opted at

    `campaign_name: Literal['asc', 'desc']`
    :   Campaign name

    `click_count: Literal['asc', 'desc']`
    :   Click count

    `company: Literal['asc', 'desc']`
    :   Company

    `company_followers: Literal['asc', 'desc']`
    :   Company followers

    `company_founded_at: Literal['asc', 'desc']`
    :   Company founded at

    `company_industry: Literal['asc', 'desc']`
    :   Company industry

    `company_linked_in: Literal['asc', 'desc']`
    :   Company linked in

    `company_linked_in_employees: Literal['asc', 'desc']`
    :   Company linked in employees

    `company_locality: Literal['asc', 'desc']`
    :   Company locality

    `company_natural: Literal['asc', 'desc']`
    :   Company natural

    `company_size: Literal['asc', 'desc']`
    :   Company size

    `company_start_date: Literal['asc', 'desc']`
    :   Company start date

    `company_type: Literal['asc', 'desc']`
    :   Company type

    `contact_histogram: Literal['asc', 'desc']`
    :   Contact histogram

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `custom1: Literal['asc', 'desc']`
    :   Custom field 1

    `custom10: Literal['asc', 'desc']`
    :   Custom field 10

    `custom100: Literal['asc', 'desc']`
    :   Custom field 100

    `custom101: Literal['asc', 'desc']`
    :   Custom field 101

    `custom102: Literal['asc', 'desc']`
    :   Custom field 102

    `custom103: Literal['asc', 'desc']`
    :   Custom field 103

    `custom104: Literal['asc', 'desc']`
    :   Custom field 104

    `custom105: Literal['asc', 'desc']`
    :   Custom field 105

    `custom106: Literal['asc', 'desc']`
    :   Custom field 106

    `custom107: Literal['asc', 'desc']`
    :   Custom field 107

    `custom108: Literal['asc', 'desc']`
    :   Custom field 108

    `custom109: Literal['asc', 'desc']`
    :   Custom field 109

    `custom11: Literal['asc', 'desc']`
    :   Custom field 11

    `custom110: Literal['asc', 'desc']`
    :   Custom field 110

    `custom111: Literal['asc', 'desc']`
    :   Custom field 111

    `custom112: Literal['asc', 'desc']`
    :   Custom field 112

    `custom113: Literal['asc', 'desc']`
    :   Custom field 113

    `custom114: Literal['asc', 'desc']`
    :   Custom field 114

    `custom115: Literal['asc', 'desc']`
    :   Custom field 115

    `custom116: Literal['asc', 'desc']`
    :   Custom field 116

    `custom117: Literal['asc', 'desc']`
    :   Custom field 117

    `custom118: Literal['asc', 'desc']`
    :   Custom field 118

    `custom119: Literal['asc', 'desc']`
    :   Custom field 119

    `custom12: Literal['asc', 'desc']`
    :   Custom field 12

    `custom120: Literal['asc', 'desc']`
    :   Custom field 120

    `custom121: Literal['asc', 'desc']`
    :   Custom field 121

    `custom122: Literal['asc', 'desc']`
    :   Custom field 122

    `custom123: Literal['asc', 'desc']`
    :   Custom field 123

    `custom124: Literal['asc', 'desc']`
    :   Custom field 124

    `custom125: Literal['asc', 'desc']`
    :   Custom field 125

    `custom126: Literal['asc', 'desc']`
    :   Custom field 126

    `custom127: Literal['asc', 'desc']`
    :   Custom field 127

    `custom128: Literal['asc', 'desc']`
    :   Custom field 128

    `custom129: Literal['asc', 'desc']`
    :   Custom field 129

    `custom13: Literal['asc', 'desc']`
    :   Custom field 13

    `custom130: Literal['asc', 'desc']`
    :   Custom field 130

    `custom131: Literal['asc', 'desc']`
    :   Custom field 131

    `custom132: Literal['asc', 'desc']`
    :   Custom field 132

    `custom133: Literal['asc', 'desc']`
    :   Custom field 133

    `custom134: Literal['asc', 'desc']`
    :   Custom field 134

    `custom135: Literal['asc', 'desc']`
    :   Custom field 135

    `custom136: Literal['asc', 'desc']`
    :   Custom field 136

    `custom137: Literal['asc', 'desc']`
    :   Custom field 137

    `custom138: Literal['asc', 'desc']`
    :   Custom field 138

    `custom139: Literal['asc', 'desc']`
    :   Custom field 139

    `custom14: Literal['asc', 'desc']`
    :   Custom field 14

    `custom140: Literal['asc', 'desc']`
    :   Custom field 140

    `custom141: Literal['asc', 'desc']`
    :   Custom field 141

    `custom142: Literal['asc', 'desc']`
    :   Custom field 142

    `custom143: Literal['asc', 'desc']`
    :   Custom field 143

    `custom144: Literal['asc', 'desc']`
    :   Custom field 144

    `custom145: Literal['asc', 'desc']`
    :   Custom field 145

    `custom146: Literal['asc', 'desc']`
    :   Custom field 146

    `custom147: Literal['asc', 'desc']`
    :   Custom field 147

    `custom148: Literal['asc', 'desc']`
    :   Custom field 148

    `custom149: Literal['asc', 'desc']`
    :   Custom field 149

    `custom15: Literal['asc', 'desc']`
    :   Custom field 15

    `custom150: Literal['asc', 'desc']`
    :   Custom field 150

    `custom16: Literal['asc', 'desc']`
    :   Custom field 16

    `custom17: Literal['asc', 'desc']`
    :   Custom field 17

    `custom18: Literal['asc', 'desc']`
    :   Custom field 18

    `custom19: Literal['asc', 'desc']`
    :   Custom field 19

    `custom2: Literal['asc', 'desc']`
    :   Custom field 2

    `custom20: Literal['asc', 'desc']`
    :   Custom field 20

    `custom21: Literal['asc', 'desc']`
    :   Custom field 21

    `custom22: Literal['asc', 'desc']`
    :   Custom field 22

    `custom23: Literal['asc', 'desc']`
    :   Custom field 23

    `custom24: Literal['asc', 'desc']`
    :   Custom field 24

    `custom25: Literal['asc', 'desc']`
    :   Custom field 25

    `custom26: Literal['asc', 'desc']`
    :   Custom field 26

    `custom27: Literal['asc', 'desc']`
    :   Custom field 27

    `custom28: Literal['asc', 'desc']`
    :   Custom field 28

    `custom29: Literal['asc', 'desc']`
    :   Custom field 29

    `custom3: Literal['asc', 'desc']`
    :   Custom field 3

    `custom30: Literal['asc', 'desc']`
    :   Custom field 30

    `custom31: Literal['asc', 'desc']`
    :   Custom field 31

    `custom32: Literal['asc', 'desc']`
    :   Custom field 32

    `custom33: Literal['asc', 'desc']`
    :   Custom field 33

    `custom34: Literal['asc', 'desc']`
    :   Custom field 34

    `custom35: Literal['asc', 'desc']`
    :   Custom field 35

    `custom36: Literal['asc', 'desc']`
    :   Custom field 36

    `custom37: Literal['asc', 'desc']`
    :   Custom field 37

    `custom38: Literal['asc', 'desc']`
    :   Custom field 38

    `custom39: Literal['asc', 'desc']`
    :   Custom field 39

    `custom4: Literal['asc', 'desc']`
    :   Custom field 4

    `custom40: Literal['asc', 'desc']`
    :   Custom field 40

    `custom41: Literal['asc', 'desc']`
    :   Custom field 41

    `custom42: Literal['asc', 'desc']`
    :   Custom field 42

    `custom43: Literal['asc', 'desc']`
    :   Custom field 43

    `custom44: Literal['asc', 'desc']`
    :   Custom field 44

    `custom45: Literal['asc', 'desc']`
    :   Custom field 45

    `custom46: Literal['asc', 'desc']`
    :   Custom field 46

    `custom47: Literal['asc', 'desc']`
    :   Custom field 47

    `custom48: Literal['asc', 'desc']`
    :   Custom field 48

    `custom49: Literal['asc', 'desc']`
    :   Custom field 49

    `custom5: Literal['asc', 'desc']`
    :   Custom field 5

    `custom50: Literal['asc', 'desc']`
    :   Custom field 50

    `custom51: Literal['asc', 'desc']`
    :   Custom field 51

    `custom52: Literal['asc', 'desc']`
    :   Custom field 52

    `custom53: Literal['asc', 'desc']`
    :   Custom field 53

    `custom54: Literal['asc', 'desc']`
    :   Custom field 54

    `custom55: Literal['asc', 'desc']`
    :   Custom field 55

    `custom56: Literal['asc', 'desc']`
    :   Custom field 56

    `custom57: Literal['asc', 'desc']`
    :   Custom field 57

    `custom58: Literal['asc', 'desc']`
    :   Custom field 58

    `custom59: Literal['asc', 'desc']`
    :   Custom field 59

    `custom6: Literal['asc', 'desc']`
    :   Custom field 6

    `custom60: Literal['asc', 'desc']`
    :   Custom field 60

    `custom61: Literal['asc', 'desc']`
    :   Custom field 61

    `custom62: Literal['asc', 'desc']`
    :   Custom field 62

    `custom63: Literal['asc', 'desc']`
    :   Custom field 63

    `custom64: Literal['asc', 'desc']`
    :   Custom field 64

    `custom65: Literal['asc', 'desc']`
    :   Custom field 65

    `custom66: Literal['asc', 'desc']`
    :   Custom field 66

    `custom67: Literal['asc', 'desc']`
    :   Custom field 67

    `custom68: Literal['asc', 'desc']`
    :   Custom field 68

    `custom69: Literal['asc', 'desc']`
    :   Custom field 69

    `custom7: Literal['asc', 'desc']`
    :   Custom field 7

    `custom70: Literal['asc', 'desc']`
    :   Custom field 70

    `custom71: Literal['asc', 'desc']`
    :   Custom field 71

    `custom72: Literal['asc', 'desc']`
    :   Custom field 72

    `custom73: Literal['asc', 'desc']`
    :   Custom field 73

    `custom74: Literal['asc', 'desc']`
    :   Custom field 74

    `custom75: Literal['asc', 'desc']`
    :   Custom field 75

    `custom76: Literal['asc', 'desc']`
    :   Custom field 76

    `custom77: Literal['asc', 'desc']`
    :   Custom field 77

    `custom78: Literal['asc', 'desc']`
    :   Custom field 78

    `custom79: Literal['asc', 'desc']`
    :   Custom field 79

    `custom8: Literal['asc', 'desc']`
    :   Custom field 8

    `custom80: Literal['asc', 'desc']`
    :   Custom field 80

    `custom81: Literal['asc', 'desc']`
    :   Custom field 81

    `custom82: Literal['asc', 'desc']`
    :   Custom field 82

    `custom83: Literal['asc', 'desc']`
    :   Custom field 83

    `custom84: Literal['asc', 'desc']`
    :   Custom field 84

    `custom85: Literal['asc', 'desc']`
    :   Custom field 85

    `custom86: Literal['asc', 'desc']`
    :   Custom field 86

    `custom87: Literal['asc', 'desc']`
    :   Custom field 87

    `custom88: Literal['asc', 'desc']`
    :   Custom field 88

    `custom89: Literal['asc', 'desc']`
    :   Custom field 89

    `custom9: Literal['asc', 'desc']`
    :   Custom field 9

    `custom90: Literal['asc', 'desc']`
    :   Custom field 90

    `custom91: Literal['asc', 'desc']`
    :   Custom field 91

    `custom92: Literal['asc', 'desc']`
    :   Custom field 92

    `custom93: Literal['asc', 'desc']`
    :   Custom field 93

    `custom94: Literal['asc', 'desc']`
    :   Custom field 94

    `custom95: Literal['asc', 'desc']`
    :   Custom field 95

    `custom96: Literal['asc', 'desc']`
    :   Custom field 96

    `custom97: Literal['asc', 'desc']`
    :   Custom field 97

    `custom98: Literal['asc', 'desc']`
    :   Custom field 98

    `custom99: Literal['asc', 'desc']`
    :   Custom field 99

    `date_of_birth: Literal['asc', 'desc']`
    :   Date of birth

    `default_plugin_mapping: Literal['asc', 'desc']`
    :   Default plugin mapping

    `degree: Literal['asc', 'desc']`
    :   Degree

    `email_addresses: Literal['asc', 'desc']`
    :   Email addresses

    `email_contacts: Literal['asc', 'desc']`
    :   Email contacts

    `email_opted_out: Literal['asc', 'desc']`
    :   Email opted out

    `emails: Literal['asc', 'desc']`
    :   Emails

    `emails_opt_status: Literal['asc', 'desc']`
    :   Emails opt status

    `emails_opted_at: Literal['asc', 'desc']`
    :   Emails opted at

    `engaged_at: Literal['asc', 'desc']`
    :   Engaged at

    `engaged_score: Literal['asc', 'desc']`
    :   Engaged score

    `event_name: Literal['asc', 'desc']`
    :   Event name

    `external_id: Literal['asc', 'desc']`
    :   External id

    `external_owner: Literal['asc', 'desc']`
    :   External owner

    `external_source: Literal['asc', 'desc']`
    :   External source

    `facebook_url: Literal['asc', 'desc']`
    :   Facebook url

    `favorites: Literal['asc', 'desc']`
    :   Favorites

    `first_name: Literal['asc', 'desc']`
    :   First name

    `gender: Literal['asc', 'desc']`
    :   Gender

    `github_url: Literal['asc', 'desc']`
    :   Github url

    `github_username: Literal['asc', 'desc']`
    :   Github username

    `google_plus_url: Literal['asc', 'desc']`
    :   Google plus url

    `graduation_date: Literal['asc', 'desc']`
    :   Graduation date

    `home_phones: Literal['asc', 'desc']`
    :   Home phones

    `id: Literal['asc', 'desc']`
    :   Unique prospect identifier

    `job_start_date: Literal['asc', 'desc']`
    :   Job start date

    `last_name: Literal['asc', 'desc']`
    :   Last name

    `linked_in_connections: Literal['asc', 'desc']`
    :   Linked in connections

    `linked_in_id: Literal['asc', 'desc']`
    :   Linked in id

    `linked_in_slug: Literal['asc', 'desc']`
    :   Linked in slug

    `linked_in_url: Literal['asc', 'desc']`
    :   Linked in url

    `mailings: Literal['asc', 'desc']`
    :   Mailings

    `middle_name: Literal['asc', 'desc']`
    :   Middle name

    `mobile_phones: Literal['asc', 'desc']`
    :   Mobile phones

    `name: Literal['asc', 'desc']`
    :   Name

    `nickname: Literal['asc', 'desc']`
    :   Nickname

    `occupation: Literal['asc', 'desc']`
    :   Occupation

    `open_count: Literal['asc', 'desc']`
    :   Open count

    `opportunities: Literal['asc', 'desc']`
    :   Opportunities

    `opportunity_prospect_roles: Literal['asc', 'desc']`
    :   Opportunity prospect roles

    `opted_out: Literal['asc', 'desc']`
    :   Opted out

    `opted_out_at: Literal['asc', 'desc']`
    :   Opted out at

    `other_phones: Literal['asc', 'desc']`
    :   Other phones

    `owner: Literal['asc', 'desc']`
    :   Owner

    `persona: Literal['asc', 'desc']`
    :   Persona

    `persona_name: Literal['asc', 'desc']`
    :   Persona name

    `personal_note1: Literal['asc', 'desc']`
    :   Personal note1

    `personal_note2: Literal['asc', 'desc']`
    :   Personal note2

    `phone_numbers: Literal['asc', 'desc']`
    :   Phone numbers

    `preferred_contact: Literal['asc', 'desc']`
    :   Preferred contact

    `quora_url: Literal['asc', 'desc']`
    :   Quora url

    `region: Literal['asc', 'desc']`
    :   Region

    `reply_count: Literal['asc', 'desc']`
    :   Reply count

    `school: Literal['asc', 'desc']`
    :   School

    `score: Literal['asc', 'desc']`
    :   Score

    `sequence_states: Literal['asc', 'desc']`
    :   Sequence states

    `sharing_team_id: Literal['asc', 'desc']`
    :   Sharing team id

    `sms_opt_status: Literal['asc', 'desc']`
    :   Sms opt status

    `sms_opted_at: Literal['asc', 'desc']`
    :   Sms opted at

    `sms_opted_out: Literal['asc', 'desc']`
    :   Sms opted out

    `source: Literal['asc', 'desc']`
    :   Source

    `specialties: Literal['asc', 'desc']`
    :   Specialties

    `stack_overflow_id: Literal['asc', 'desc']`
    :   Stack overflow id

    `stack_overflow_url: Literal['asc', 'desc']`
    :   Stack overflow url

    `stage: Literal['asc', 'desc']`
    :   Stage

    `stage_name: Literal['asc', 'desc']`
    :   Stage name

    `tags: Literal['asc', 'desc']`
    :   Tags

    `tasks: Literal['asc', 'desc']`
    :   Tasks

    `time_zone: Literal['asc', 'desc']`
    :   Time zone

    `time_zone_iana: Literal['asc', 'desc']`
    :   Time zone iana

    `time_zone_inferred: Literal['asc', 'desc']`
    :   Time zone inferred

    `title: Literal['asc', 'desc']`
    :   Title

    `touched_at: Literal['asc', 'desc']`
    :   Touched at

    `trashed_at: Literal['asc', 'desc']`
    :   Trashed at

    `trashed_by_account: Literal['asc', 'desc']`
    :   Trashed by account

    `twitter_url: Literal['asc', 'desc']`
    :   Twitter url

    `twitter_username: Literal['asc', 'desc']`
    :   Twitter username

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

    `updater_id: Literal['asc', 'desc']`
    :   Updater id

    `updater_type: Literal['asc', 'desc']`
    :   Updater type

    `voip_phones: Literal['asc', 'desc']`
    :   Voip phones

    `website_url1: Literal['asc', 'desc']`
    :   Website url1

    `website_url2: Literal['asc', 'desc']`
    :   Website url2

    `website_url3: Literal['asc', 'desc']`
    :   Website url3

    `work_phones: Literal['asc', 'desc']`
    :   Work phones

<a id="ProspectsStartswithCondition"></a>

`ProspectsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.ProspectsStringFilter`
    :   The type of the None singleton.

<a id="ProspectsStringFilter"></a>

`ProspectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   Account

    `account_name: str`
    :   Account name

    `active_sequence_states: str`
    :   Active sequence states

    `added_at: str`
    :   Added at

    `address_city: str`
    :   Address city

    `address_country: str`
    :   Address country

    `address_state: str`
    :   Address state

    `address_street: str`
    :   Address street

    `address_street2: str`
    :   Address street2

    `address_zip: str`
    :   Address zip

    `angel_list_url: str`
    :   Angel list url

    `assigned_teams: str`
    :   Assigned teams

    `assigned_users: str`
    :   Assigned users

    `available_at: str`
    :   Available at

    `batches: str`
    :   Batches

    `call_opted_out: str`
    :   Call opted out

    `calls: str`
    :   Calls

    `calls_opt_status: str`
    :   Calls opt status

    `calls_opted_at: str`
    :   Calls opted at

    `campaign_name: str`
    :   Campaign name

    `click_count: str`
    :   Click count

    `company: str`
    :   Company

    `company_followers: str`
    :   Company followers

    `company_founded_at: str`
    :   Company founded at

    `company_industry: str`
    :   Company industry

    `company_linked_in: str`
    :   Company linked in

    `company_linked_in_employees: str`
    :   Company linked in employees

    `company_locality: str`
    :   Company locality

    `company_natural: str`
    :   Company natural

    `company_size: str`
    :   Company size

    `company_start_date: str`
    :   Company start date

    `company_type: str`
    :   Company type

    `contact_histogram: str`
    :   Contact histogram

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `custom1: str`
    :   Custom field 1

    `custom10: str`
    :   Custom field 10

    `custom100: str`
    :   Custom field 100

    `custom101: str`
    :   Custom field 101

    `custom102: str`
    :   Custom field 102

    `custom103: str`
    :   Custom field 103

    `custom104: str`
    :   Custom field 104

    `custom105: str`
    :   Custom field 105

    `custom106: str`
    :   Custom field 106

    `custom107: str`
    :   Custom field 107

    `custom108: str`
    :   Custom field 108

    `custom109: str`
    :   Custom field 109

    `custom11: str`
    :   Custom field 11

    `custom110: str`
    :   Custom field 110

    `custom111: str`
    :   Custom field 111

    `custom112: str`
    :   Custom field 112

    `custom113: str`
    :   Custom field 113

    `custom114: str`
    :   Custom field 114

    `custom115: str`
    :   Custom field 115

    `custom116: str`
    :   Custom field 116

    `custom117: str`
    :   Custom field 117

    `custom118: str`
    :   Custom field 118

    `custom119: str`
    :   Custom field 119

    `custom12: str`
    :   Custom field 12

    `custom120: str`
    :   Custom field 120

    `custom121: str`
    :   Custom field 121

    `custom122: str`
    :   Custom field 122

    `custom123: str`
    :   Custom field 123

    `custom124: str`
    :   Custom field 124

    `custom125: str`
    :   Custom field 125

    `custom126: str`
    :   Custom field 126

    `custom127: str`
    :   Custom field 127

    `custom128: str`
    :   Custom field 128

    `custom129: str`
    :   Custom field 129

    `custom13: str`
    :   Custom field 13

    `custom130: str`
    :   Custom field 130

    `custom131: str`
    :   Custom field 131

    `custom132: str`
    :   Custom field 132

    `custom133: str`
    :   Custom field 133

    `custom134: str`
    :   Custom field 134

    `custom135: str`
    :   Custom field 135

    `custom136: str`
    :   Custom field 136

    `custom137: str`
    :   Custom field 137

    `custom138: str`
    :   Custom field 138

    `custom139: str`
    :   Custom field 139

    `custom14: str`
    :   Custom field 14

    `custom140: str`
    :   Custom field 140

    `custom141: str`
    :   Custom field 141

    `custom142: str`
    :   Custom field 142

    `custom143: str`
    :   Custom field 143

    `custom144: str`
    :   Custom field 144

    `custom145: str`
    :   Custom field 145

    `custom146: str`
    :   Custom field 146

    `custom147: str`
    :   Custom field 147

    `custom148: str`
    :   Custom field 148

    `custom149: str`
    :   Custom field 149

    `custom15: str`
    :   Custom field 15

    `custom150: str`
    :   Custom field 150

    `custom16: str`
    :   Custom field 16

    `custom17: str`
    :   Custom field 17

    `custom18: str`
    :   Custom field 18

    `custom19: str`
    :   Custom field 19

    `custom2: str`
    :   Custom field 2

    `custom20: str`
    :   Custom field 20

    `custom21: str`
    :   Custom field 21

    `custom22: str`
    :   Custom field 22

    `custom23: str`
    :   Custom field 23

    `custom24: str`
    :   Custom field 24

    `custom25: str`
    :   Custom field 25

    `custom26: str`
    :   Custom field 26

    `custom27: str`
    :   Custom field 27

    `custom28: str`
    :   Custom field 28

    `custom29: str`
    :   Custom field 29

    `custom3: str`
    :   Custom field 3

    `custom30: str`
    :   Custom field 30

    `custom31: str`
    :   Custom field 31

    `custom32: str`
    :   Custom field 32

    `custom33: str`
    :   Custom field 33

    `custom34: str`
    :   Custom field 34

    `custom35: str`
    :   Custom field 35

    `custom36: str`
    :   Custom field 36

    `custom37: str`
    :   Custom field 37

    `custom38: str`
    :   Custom field 38

    `custom39: str`
    :   Custom field 39

    `custom4: str`
    :   Custom field 4

    `custom40: str`
    :   Custom field 40

    `custom41: str`
    :   Custom field 41

    `custom42: str`
    :   Custom field 42

    `custom43: str`
    :   Custom field 43

    `custom44: str`
    :   Custom field 44

    `custom45: str`
    :   Custom field 45

    `custom46: str`
    :   Custom field 46

    `custom47: str`
    :   Custom field 47

    `custom48: str`
    :   Custom field 48

    `custom49: str`
    :   Custom field 49

    `custom5: str`
    :   Custom field 5

    `custom50: str`
    :   Custom field 50

    `custom51: str`
    :   Custom field 51

    `custom52: str`
    :   Custom field 52

    `custom53: str`
    :   Custom field 53

    `custom54: str`
    :   Custom field 54

    `custom55: str`
    :   Custom field 55

    `custom56: str`
    :   Custom field 56

    `custom57: str`
    :   Custom field 57

    `custom58: str`
    :   Custom field 58

    `custom59: str`
    :   Custom field 59

    `custom6: str`
    :   Custom field 6

    `custom60: str`
    :   Custom field 60

    `custom61: str`
    :   Custom field 61

    `custom62: str`
    :   Custom field 62

    `custom63: str`
    :   Custom field 63

    `custom64: str`
    :   Custom field 64

    `custom65: str`
    :   Custom field 65

    `custom66: str`
    :   Custom field 66

    `custom67: str`
    :   Custom field 67

    `custom68: str`
    :   Custom field 68

    `custom69: str`
    :   Custom field 69

    `custom7: str`
    :   Custom field 7

    `custom70: str`
    :   Custom field 70

    `custom71: str`
    :   Custom field 71

    `custom72: str`
    :   Custom field 72

    `custom73: str`
    :   Custom field 73

    `custom74: str`
    :   Custom field 74

    `custom75: str`
    :   Custom field 75

    `custom76: str`
    :   Custom field 76

    `custom77: str`
    :   Custom field 77

    `custom78: str`
    :   Custom field 78

    `custom79: str`
    :   Custom field 79

    `custom8: str`
    :   Custom field 8

    `custom80: str`
    :   Custom field 80

    `custom81: str`
    :   Custom field 81

    `custom82: str`
    :   Custom field 82

    `custom83: str`
    :   Custom field 83

    `custom84: str`
    :   Custom field 84

    `custom85: str`
    :   Custom field 85

    `custom86: str`
    :   Custom field 86

    `custom87: str`
    :   Custom field 87

    `custom88: str`
    :   Custom field 88

    `custom89: str`
    :   Custom field 89

    `custom9: str`
    :   Custom field 9

    `custom90: str`
    :   Custom field 90

    `custom91: str`
    :   Custom field 91

    `custom92: str`
    :   Custom field 92

    `custom93: str`
    :   Custom field 93

    `custom94: str`
    :   Custom field 94

    `custom95: str`
    :   Custom field 95

    `custom96: str`
    :   Custom field 96

    `custom97: str`
    :   Custom field 97

    `custom98: str`
    :   Custom field 98

    `custom99: str`
    :   Custom field 99

    `date_of_birth: str`
    :   Date of birth

    `default_plugin_mapping: str`
    :   Default plugin mapping

    `degree: str`
    :   Degree

    `email_addresses: str`
    :   Email addresses

    `email_contacts: str`
    :   Email contacts

    `email_opted_out: str`
    :   Email opted out

    `emails: str`
    :   Emails

    `emails_opt_status: str`
    :   Emails opt status

    `emails_opted_at: str`
    :   Emails opted at

    `engaged_at: str`
    :   Engaged at

    `engaged_score: str`
    :   Engaged score

    `event_name: str`
    :   Event name

    `external_id: str`
    :   External id

    `external_owner: str`
    :   External owner

    `external_source: str`
    :   External source

    `facebook_url: str`
    :   Facebook url

    `favorites: str`
    :   Favorites

    `first_name: str`
    :   First name

    `gender: str`
    :   Gender

    `github_url: str`
    :   Github url

    `github_username: str`
    :   Github username

    `google_plus_url: str`
    :   Google plus url

    `graduation_date: str`
    :   Graduation date

    `home_phones: str`
    :   Home phones

    `id: str`
    :   Unique prospect identifier

    `job_start_date: str`
    :   Job start date

    `last_name: str`
    :   Last name

    `linked_in_connections: str`
    :   Linked in connections

    `linked_in_id: str`
    :   Linked in id

    `linked_in_slug: str`
    :   Linked in slug

    `linked_in_url: str`
    :   Linked in url

    `mailings: str`
    :   Mailings

    `middle_name: str`
    :   Middle name

    `mobile_phones: str`
    :   Mobile phones

    `name: str`
    :   Name

    `nickname: str`
    :   Nickname

    `occupation: str`
    :   Occupation

    `open_count: str`
    :   Open count

    `opportunities: str`
    :   Opportunities

    `opportunity_prospect_roles: str`
    :   Opportunity prospect roles

    `opted_out: str`
    :   Opted out

    `opted_out_at: str`
    :   Opted out at

    `other_phones: str`
    :   Other phones

    `owner: str`
    :   Owner

    `persona: str`
    :   Persona

    `persona_name: str`
    :   Persona name

    `personal_note1: str`
    :   Personal note1

    `personal_note2: str`
    :   Personal note2

    `phone_numbers: str`
    :   Phone numbers

    `preferred_contact: str`
    :   Preferred contact

    `quora_url: str`
    :   Quora url

    `region: str`
    :   Region

    `reply_count: str`
    :   Reply count

    `school: str`
    :   School

    `score: str`
    :   Score

    `sequence_states: str`
    :   Sequence states

    `sharing_team_id: str`
    :   Sharing team id

    `sms_opt_status: str`
    :   Sms opt status

    `sms_opted_at: str`
    :   Sms opted at

    `sms_opted_out: str`
    :   Sms opted out

    `source: str`
    :   Source

    `specialties: str`
    :   Specialties

    `stack_overflow_id: str`
    :   Stack overflow id

    `stack_overflow_url: str`
    :   Stack overflow url

    `stage: str`
    :   Stage

    `stage_name: str`
    :   Stage name

    `tags: str`
    :   Tags

    `tasks: str`
    :   Tasks

    `time_zone: str`
    :   Time zone

    `time_zone_iana: str`
    :   Time zone iana

    `time_zone_inferred: str`
    :   Time zone inferred

    `title: str`
    :   Title

    `touched_at: str`
    :   Touched at

    `trashed_at: str`
    :   Trashed at

    `trashed_by_account: str`
    :   Trashed by account

    `twitter_url: str`
    :   Twitter url

    `twitter_username: str`
    :   Twitter username

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

    `updater_id: str`
    :   Updater id

    `updater_type: str`
    :   Updater type

    `voip_phones: str`
    :   Voip phones

    `website_url1: str`
    :   Website url1

    `website_url2: str`
    :   Website url2

    `website_url3: str`
    :   Website url3

    `work_phones: str`
    :   Work phones

<a id="SequenceStatesAndCondition"></a>

`SequenceStatesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.SequenceStatesEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesInCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAnyCondition]`
    :   The type of the None singleton.

<a id="SequenceStatesAnyCondition"></a>

`SequenceStatesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAnyValueFilter`
    :   The type of the None singleton.

<a id="SequenceStatesAnyValueFilter"></a>

`SequenceStatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Any`
    :   Account

    `active_at: Any`
    :   Active at

    `active_step_mailings: Any`
    :   Active step mailings

    `active_step_tasks: Any`
    :   Active step tasks

    `bounce_count: Any`
    :   Bounce count

    `call_completed_at: Any`
    :   Call completed at

    `calls: Any`
    :   Calls

    `click_count: Any`
    :   Click count

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `deliver_count: Any`
    :   Deliver count

    `error_reason: Any`
    :   Error reason

    `failure_count: Any`
    :   Failure count

    `id: Any`
    :   Unique sequence state identifier

    `mailbox: Any`
    :   Mailbox

    `mailings: Any`
    :   Mailings

    `negative_reply_count: Any`
    :   Negative reply count

    `neutral_reply_count: Any`
    :   Neutral reply count

    `open_count: Any`
    :   Open count

    `opportunity: Any`
    :   Opportunity

    `opt_out_count: Any`
    :   Opt out count

    `pause_reason: Any`
    :   Pause reason

    `positive_reply_count: Any`
    :   Positive reply count

    `prospect: Any`
    :   Prospect

    `replied_at: Any`
    :   Replied at

    `reply_count: Any`
    :   Reply count

    `schedule_count: Any`
    :   Schedule count

    `sequence: Any`
    :   Sequence

    `sequence_step: Any`
    :   Sequence step

    `state: Any`
    :   State

    `state_changed_at: Any`
    :   State changed at

    `tasks: Any`
    :   Tasks

    `updated_at: Any`
    :   Updated at

<a id="SequenceStatesArrayContainsCondition"></a>

`SequenceStatesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAnyValueFilter`
    :   The type of the None singleton.

<a id="SequenceStatesContainsCondition"></a>

`SequenceStatesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAnyValueFilter`
    :   The type of the None singleton.

<a id="SequenceStatesEndswithCondition"></a>

`SequenceStatesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesStringFilter`
    :   The type of the None singleton.

<a id="SequenceStatesEqCondition"></a>

`SequenceStatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStatesFuzzyCondition"></a>

`SequenceStatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesStringFilter`
    :   The type of the None singleton.

<a id="SequenceStatesGetParams"></a>

`SequenceStatesGetParams(*args, **kwargs)`
:   Parameters for sequence_states.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SequenceStatesGtCondition"></a>

`SequenceStatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStatesGteCondition"></a>

`SequenceStatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStatesInCondition"></a>

`SequenceStatesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesInFilter`
    :   The type of the None singleton.

<a id="SequenceStatesInFilter"></a>

`SequenceStatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: list[list[typing.Any]]`
    :   Account

    `active_at: list[str]`
    :   Active at

    `active_step_mailings: list[list[typing.Any]]`
    :   Active step mailings

    `active_step_tasks: list[list[typing.Any]]`
    :   Active step tasks

    `bounce_count: list[int]`
    :   Bounce count

    `call_completed_at: list[str]`
    :   Call completed at

    `calls: list[list[typing.Any]]`
    :   Calls

    `click_count: list[int]`
    :   Click count

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `deliver_count: list[int]`
    :   Deliver count

    `error_reason: list[str]`
    :   Error reason

    `failure_count: list[int]`
    :   Failure count

    `id: list[int]`
    :   Unique sequence state identifier

    `mailbox: list[list[typing.Any]]`
    :   Mailbox

    `mailings: list[list[typing.Any]]`
    :   Mailings

    `negative_reply_count: list[int]`
    :   Negative reply count

    `neutral_reply_count: list[int]`
    :   Neutral reply count

    `open_count: list[int]`
    :   Open count

    `opportunity: list[list[typing.Any]]`
    :   Opportunity

    `opt_out_count: list[int]`
    :   Opt out count

    `pause_reason: list[str]`
    :   Pause reason

    `positive_reply_count: list[int]`
    :   Positive reply count

    `prospect: list[list[typing.Any]]`
    :   Prospect

    `replied_at: list[str]`
    :   Replied at

    `reply_count: list[int]`
    :   Reply count

    `schedule_count: list[int]`
    :   Schedule count

    `sequence: list[list[typing.Any]]`
    :   Sequence

    `sequence_step: list[list[typing.Any]]`
    :   Sequence step

    `state: list[str]`
    :   State

    `state_changed_at: list[str]`
    :   State changed at

    `tasks: list[list[typing.Any]]`
    :   Tasks

    `updated_at: list[str]`
    :   Updated at

<a id="SequenceStatesKeywordCondition"></a>

`SequenceStatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesStringFilter`
    :   The type of the None singleton.

<a id="SequenceStatesListParams"></a>

`SequenceStatesListParams(*args, **kwargs)`
:   Parameters for sequence_states.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="SequenceStatesLtCondition"></a>

`SequenceStatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStatesLteCondition"></a>

`SequenceStatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStatesNeqCondition"></a>

`SequenceStatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStatesNotCondition"></a>

`SequenceStatesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesInCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAnyCondition`
    :   The type of the None singleton.

<a id="SequenceStatesOrCondition"></a>

`SequenceStatesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.SequenceStatesEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesInCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAnyCondition]`
    :   The type of the None singleton.

<a id="SequenceStatesSearchFilter"></a>

`SequenceStatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering sequence_states search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="SequenceStatesSearchQuery"></a>

`SequenceStatesSearchQuery(*args, **kwargs)`
:   Search query for sequence_states entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesInCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.SequenceStatesSortFilter]`
    :   The type of the None singleton.

<a id="SequenceStatesSortFilter"></a>

`SequenceStatesSortFilter(*args, **kwargs)`
:   Available fields for sorting sequence_states search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Literal['asc', 'desc']`
    :   Account

    `active_at: Literal['asc', 'desc']`
    :   Active at

    `active_step_mailings: Literal['asc', 'desc']`
    :   Active step mailings

    `active_step_tasks: Literal['asc', 'desc']`
    :   Active step tasks

    `bounce_count: Literal['asc', 'desc']`
    :   Bounce count

    `call_completed_at: Literal['asc', 'desc']`
    :   Call completed at

    `calls: Literal['asc', 'desc']`
    :   Calls

    `click_count: Literal['asc', 'desc']`
    :   Click count

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `deliver_count: Literal['asc', 'desc']`
    :   Deliver count

    `error_reason: Literal['asc', 'desc']`
    :   Error reason

    `failure_count: Literal['asc', 'desc']`
    :   Failure count

    `id: Literal['asc', 'desc']`
    :   Unique sequence state identifier

    `mailbox: Literal['asc', 'desc']`
    :   Mailbox

    `mailings: Literal['asc', 'desc']`
    :   Mailings

    `negative_reply_count: Literal['asc', 'desc']`
    :   Negative reply count

    `neutral_reply_count: Literal['asc', 'desc']`
    :   Neutral reply count

    `open_count: Literal['asc', 'desc']`
    :   Open count

    `opportunity: Literal['asc', 'desc']`
    :   Opportunity

    `opt_out_count: Literal['asc', 'desc']`
    :   Opt out count

    `pause_reason: Literal['asc', 'desc']`
    :   Pause reason

    `positive_reply_count: Literal['asc', 'desc']`
    :   Positive reply count

    `prospect: Literal['asc', 'desc']`
    :   Prospect

    `replied_at: Literal['asc', 'desc']`
    :   Replied at

    `reply_count: Literal['asc', 'desc']`
    :   Reply count

    `schedule_count: Literal['asc', 'desc']`
    :   Schedule count

    `sequence: Literal['asc', 'desc']`
    :   Sequence

    `sequence_step: Literal['asc', 'desc']`
    :   Sequence step

    `state: Literal['asc', 'desc']`
    :   State

    `state_changed_at: Literal['asc', 'desc']`
    :   State changed at

    `tasks: Literal['asc', 'desc']`
    :   Tasks

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

<a id="SequenceStatesStartswithCondition"></a>

`SequenceStatesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.SequenceStatesStringFilter`
    :   The type of the None singleton.

<a id="SequenceStatesStringFilter"></a>

`SequenceStatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   Account

    `active_at: str`
    :   Active at

    `active_step_mailings: str`
    :   Active step mailings

    `active_step_tasks: str`
    :   Active step tasks

    `bounce_count: str`
    :   Bounce count

    `call_completed_at: str`
    :   Call completed at

    `calls: str`
    :   Calls

    `click_count: str`
    :   Click count

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `deliver_count: str`
    :   Deliver count

    `error_reason: str`
    :   Error reason

    `failure_count: str`
    :   Failure count

    `id: str`
    :   Unique sequence state identifier

    `mailbox: str`
    :   Mailbox

    `mailings: str`
    :   Mailings

    `negative_reply_count: str`
    :   Negative reply count

    `neutral_reply_count: str`
    :   Neutral reply count

    `open_count: str`
    :   Open count

    `opportunity: str`
    :   Opportunity

    `opt_out_count: str`
    :   Opt out count

    `pause_reason: str`
    :   Pause reason

    `positive_reply_count: str`
    :   Positive reply count

    `prospect: str`
    :   Prospect

    `replied_at: str`
    :   Replied at

    `reply_count: str`
    :   Reply count

    `schedule_count: str`
    :   Schedule count

    `sequence: str`
    :   Sequence

    `sequence_step: str`
    :   Sequence step

    `state: str`
    :   State

    `state_changed_at: str`
    :   State changed at

    `tasks: str`
    :   Tasks

    `updated_at: str`
    :   Updated at

<a id="SequenceStepsAndCondition"></a>

`SequenceStepsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.SequenceStepsEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsInCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAnyCondition]`
    :   The type of the None singleton.

<a id="SequenceStepsAnyCondition"></a>

`SequenceStepsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAnyValueFilter`
    :   The type of the None singleton.

<a id="SequenceStepsAnyValueFilter"></a>

`SequenceStepsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bounce_count: Any`
    :   Bounce count

    `call_purpose: Any`
    :   Call purpose

    `calls: Any`
    :   Calls

    `click_count: Any`
    :   Click count

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `date: Any`
    :   Date

    `deliver_count: Any`
    :   Deliver count

    `display_name: Any`
    :   Display name

    `failure_count: Any`
    :   Failure count

    `id: Any`
    :   Unique sequence step identifier

    `interval: Any`
    :   Interval

    `mailings: Any`
    :   Mailings

    `negative_reply_count: Any`
    :   Negative reply count

    `neutral_reply_count: Any`
    :   Neutral reply count

    `open_count: Any`
    :   Open count

    `opt_out_count: Any`
    :   Opt out count

    `order: Any`
    :   Order

    `positive_reply_count: Any`
    :   Positive reply count

    `reply_count: Any`
    :   Reply count

    `schedule_count: Any`
    :   Schedule count

    `sequence: Any`
    :   Sequence

    `sequence_templates: Any`
    :   Sequence templates

    `step_type: Any`
    :   Step type

    `task_auto_display: Any`
    :   Task auto display

    `task_priority: Any`
    :   Task priority

    `tasks: Any`
    :   Tasks

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

<a id="SequenceStepsArrayContainsCondition"></a>

`SequenceStepsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAnyValueFilter`
    :   The type of the None singleton.

<a id="SequenceStepsContainsCondition"></a>

`SequenceStepsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAnyValueFilter`
    :   The type of the None singleton.

<a id="SequenceStepsEndswithCondition"></a>

`SequenceStepsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsStringFilter`
    :   The type of the None singleton.

<a id="SequenceStepsEqCondition"></a>

`SequenceStepsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStepsFuzzyCondition"></a>

`SequenceStepsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsStringFilter`
    :   The type of the None singleton.

<a id="SequenceStepsGetParams"></a>

`SequenceStepsGetParams(*args, **kwargs)`
:   Parameters for sequence_steps.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SequenceStepsGtCondition"></a>

`SequenceStepsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStepsGteCondition"></a>

`SequenceStepsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStepsInCondition"></a>

`SequenceStepsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsInFilter`
    :   The type of the None singleton.

<a id="SequenceStepsInFilter"></a>

`SequenceStepsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bounce_count: list[int]`
    :   Bounce count

    `call_purpose: list[list[typing.Any]]`
    :   Call purpose

    `calls: list[list[typing.Any]]`
    :   Calls

    `click_count: list[int]`
    :   Click count

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `date: list[str]`
    :   Date

    `deliver_count: list[int]`
    :   Deliver count

    `display_name: list[str]`
    :   Display name

    `failure_count: list[int]`
    :   Failure count

    `id: list[int]`
    :   Unique sequence step identifier

    `interval: list[int]`
    :   Interval

    `mailings: list[list[typing.Any]]`
    :   Mailings

    `negative_reply_count: list[int]`
    :   Negative reply count

    `neutral_reply_count: list[int]`
    :   Neutral reply count

    `open_count: list[int]`
    :   Open count

    `opt_out_count: list[int]`
    :   Opt out count

    `order: list[int]`
    :   Order

    `positive_reply_count: list[int]`
    :   Positive reply count

    `reply_count: list[int]`
    :   Reply count

    `schedule_count: list[int]`
    :   Schedule count

    `sequence: list[list[typing.Any]]`
    :   Sequence

    `sequence_templates: list[list[typing.Any]]`
    :   Sequence templates

    `step_type: list[str]`
    :   Step type

    `task_auto_display: list[str]`
    :   Task auto display

    `task_priority: list[list[typing.Any]]`
    :   Task priority

    `tasks: list[list[typing.Any]]`
    :   Tasks

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

<a id="SequenceStepsKeywordCondition"></a>

`SequenceStepsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsStringFilter`
    :   The type of the None singleton.

<a id="SequenceStepsListParams"></a>

`SequenceStepsListParams(*args, **kwargs)`
:   Parameters for sequence_steps.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="SequenceStepsLtCondition"></a>

`SequenceStepsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStepsLteCondition"></a>

`SequenceStepsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStepsNeqCondition"></a>

`SequenceStepsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsSearchFilter`
    :   The type of the None singleton.

<a id="SequenceStepsNotCondition"></a>

`SequenceStepsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsInCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAnyCondition`
    :   The type of the None singleton.

<a id="SequenceStepsOrCondition"></a>

`SequenceStepsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.SequenceStepsEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsInCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAnyCondition]`
    :   The type of the None singleton.

<a id="SequenceStepsSearchFilter"></a>

`SequenceStepsSearchFilter(*args, **kwargs)`
:   Available fields for filtering sequence_steps search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="SequenceStepsSearchQuery"></a>

`SequenceStepsSearchQuery(*args, **kwargs)`
:   Search query for sequence_steps entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsInCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequenceStepsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.SequenceStepsSortFilter]`
    :   The type of the None singleton.

<a id="SequenceStepsSortFilter"></a>

`SequenceStepsSortFilter(*args, **kwargs)`
:   Available fields for sorting sequence_steps search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bounce_count: Literal['asc', 'desc']`
    :   Bounce count

    `call_purpose: Literal['asc', 'desc']`
    :   Call purpose

    `calls: Literal['asc', 'desc']`
    :   Calls

    `click_count: Literal['asc', 'desc']`
    :   Click count

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `date: Literal['asc', 'desc']`
    :   Date

    `deliver_count: Literal['asc', 'desc']`
    :   Deliver count

    `display_name: Literal['asc', 'desc']`
    :   Display name

    `failure_count: Literal['asc', 'desc']`
    :   Failure count

    `id: Literal['asc', 'desc']`
    :   Unique sequence step identifier

    `interval: Literal['asc', 'desc']`
    :   Interval

    `mailings: Literal['asc', 'desc']`
    :   Mailings

    `negative_reply_count: Literal['asc', 'desc']`
    :   Negative reply count

    `neutral_reply_count: Literal['asc', 'desc']`
    :   Neutral reply count

    `open_count: Literal['asc', 'desc']`
    :   Open count

    `opt_out_count: Literal['asc', 'desc']`
    :   Opt out count

    `order: Literal['asc', 'desc']`
    :   Order

    `positive_reply_count: Literal['asc', 'desc']`
    :   Positive reply count

    `reply_count: Literal['asc', 'desc']`
    :   Reply count

    `schedule_count: Literal['asc', 'desc']`
    :   Schedule count

    `sequence: Literal['asc', 'desc']`
    :   Sequence

    `sequence_templates: Literal['asc', 'desc']`
    :   Sequence templates

    `step_type: Literal['asc', 'desc']`
    :   Step type

    `task_auto_display: Literal['asc', 'desc']`
    :   Task auto display

    `task_priority: Literal['asc', 'desc']`
    :   Task priority

    `tasks: Literal['asc', 'desc']`
    :   Tasks

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

<a id="SequenceStepsStartswithCondition"></a>

`SequenceStepsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.SequenceStepsStringFilter`
    :   The type of the None singleton.

<a id="SequenceStepsStringFilter"></a>

`SequenceStepsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bounce_count: str`
    :   Bounce count

    `call_purpose: str`
    :   Call purpose

    `calls: str`
    :   Calls

    `click_count: str`
    :   Click count

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `date: str`
    :   Date

    `deliver_count: str`
    :   Deliver count

    `display_name: str`
    :   Display name

    `failure_count: str`
    :   Failure count

    `id: str`
    :   Unique sequence step identifier

    `interval: str`
    :   Interval

    `mailings: str`
    :   Mailings

    `negative_reply_count: str`
    :   Negative reply count

    `neutral_reply_count: str`
    :   Neutral reply count

    `open_count: str`
    :   Open count

    `opt_out_count: str`
    :   Opt out count

    `order: str`
    :   Order

    `positive_reply_count: str`
    :   Positive reply count

    `reply_count: str`
    :   Reply count

    `schedule_count: str`
    :   Schedule count

    `sequence: str`
    :   Sequence

    `sequence_templates: str`
    :   Sequence templates

    `step_type: str`
    :   Step type

    `task_auto_display: str`
    :   Task auto display

    `task_priority: str`
    :   Task priority

    `tasks: str`
    :   Tasks

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

<a id="SequencesAndCondition"></a>

`SequencesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.SequencesEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesInCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesAnyCondition]`
    :   The type of the None singleton.

<a id="SequencesAnyCondition"></a>

`SequencesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.SequencesAnyValueFilter`
    :   The type of the None singleton.

<a id="SequencesAnyValueFilter"></a>

`SequencesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `automation_percentage: Any`
    :   Automation percentage

    `bounce_count: Any`
    :   Bounce count

    `calls: Any`
    :   Calls

    `click_count: Any`
    :   Click count

    `content_category_memberships: Any`
    :   Content category memberships

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `deliver_count: Any`
    :   Deliver count

    `description: Any`
    :   Description

    `duration_in_days: Any`
    :   Duration in days

    `enabled: Any`
    :   Enabled

    `enabled_at: Any`
    :   Enabled at

    `failure_count: Any`
    :   Failure count

    `finish_on_reply: Any`
    :   Finish on reply

    `id: Any`
    :   Unique sequence identifier

    `last_used_at: Any`
    :   Last used at

    `locked: Any`
    :   Locked

    `locked_at: Any`
    :   Locked at

    `mailings: Any`
    :   Mailings

    `max_activations: Any`
    :   Max activations

    `name: Any`
    :   Name

    `negative_reply_count: Any`
    :   Negative reply count

    `neutral_reply_count: Any`
    :   Neutral reply count

    `num_contacted_prospects: Any`
    :   Num contacted prospects

    `num_replied_prospects: Any`
    :   Num replied prospects

    `open_count: Any`
    :   Open count

    `opt_out_count: Any`
    :   Opt out count

    `owner: Any`
    :   Owner

    `positive_reply_count: Any`
    :   Positive reply count

    `primary_reply_action: Any`
    :   Primary reply action

    `primary_reply_pause_duration: Any`
    :   Primary reply pause duration

    `reply_count: Any`
    :   Reply count

    `ruleset: Any`
    :   Ruleset

    `schedule: Any`
    :   Schedule

    `schedule_count: Any`
    :   Schedule count

    `schedule_interval_type: Any`
    :   Schedule interval type

    `secondary_reply_action: Any`
    :   Secondary reply action

    `secondary_reply_pause_duration: Any`
    :   Secondary reply pause duration

    `sequence_states: Any`
    :   Sequence states

    `sequence_step_count: Any`
    :   Sequence step count

    `sequence_steps: Any`
    :   Sequence steps

    `sequence_type: Any`
    :   Sequence type

    `share_type: Any`
    :   Share type

    `tags: Any`
    :   Tags

    `tasks: Any`
    :   Tasks

    `throttle_capacity: Any`
    :   Throttle capacity

    `throttle_max_adds_per_day: Any`
    :   Throttle max adds per day

    `throttle_paused: Any`
    :   Throttle paused

    `throttle_paused_at: Any`
    :   Throttle paused at

    `transactional: Any`
    :   Transactional

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

<a id="SequencesArrayContainsCondition"></a>

`SequencesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.SequencesAnyValueFilter`
    :   The type of the None singleton.

<a id="SequencesContainsCondition"></a>

`SequencesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.SequencesAnyValueFilter`
    :   The type of the None singleton.

<a id="SequencesEndswithCondition"></a>

`SequencesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.SequencesStringFilter`
    :   The type of the None singleton.

<a id="SequencesEqCondition"></a>

`SequencesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.SequencesSearchFilter`
    :   The type of the None singleton.

<a id="SequencesFuzzyCondition"></a>

`SequencesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.SequencesStringFilter`
    :   The type of the None singleton.

<a id="SequencesGetParams"></a>

`SequencesGetParams(*args, **kwargs)`
:   Parameters for sequences.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SequencesGtCondition"></a>

`SequencesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.SequencesSearchFilter`
    :   The type of the None singleton.

<a id="SequencesGteCondition"></a>

`SequencesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.SequencesSearchFilter`
    :   The type of the None singleton.

<a id="SequencesInCondition"></a>

`SequencesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.SequencesInFilter`
    :   The type of the None singleton.

<a id="SequencesInFilter"></a>

`SequencesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `automation_percentage: list[float]`
    :   Automation percentage

    `bounce_count: list[int]`
    :   Bounce count

    `calls: list[list[typing.Any]]`
    :   Calls

    `click_count: list[int]`
    :   Click count

    `content_category_memberships: list[list[typing.Any]]`
    :   Content category memberships

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `deliver_count: list[int]`
    :   Deliver count

    `description: list[str]`
    :   Description

    `duration_in_days: list[int]`
    :   Duration in days

    `enabled: list[bool]`
    :   Enabled

    `enabled_at: list[str]`
    :   Enabled at

    `failure_count: list[int]`
    :   Failure count

    `finish_on_reply: list[bool]`
    :   Finish on reply

    `id: list[int]`
    :   Unique sequence identifier

    `last_used_at: list[str]`
    :   Last used at

    `locked: list[bool]`
    :   Locked

    `locked_at: list[str]`
    :   Locked at

    `mailings: list[list[typing.Any]]`
    :   Mailings

    `max_activations: list[int]`
    :   Max activations

    `name: list[str]`
    :   Name

    `negative_reply_count: list[int]`
    :   Negative reply count

    `neutral_reply_count: list[int]`
    :   Neutral reply count

    `num_contacted_prospects: list[int]`
    :   Num contacted prospects

    `num_replied_prospects: list[int]`
    :   Num replied prospects

    `open_count: list[int]`
    :   Open count

    `opt_out_count: list[int]`
    :   Opt out count

    `owner: list[list[typing.Any]]`
    :   Owner

    `positive_reply_count: list[int]`
    :   Positive reply count

    `primary_reply_action: list[str]`
    :   Primary reply action

    `primary_reply_pause_duration: list[int]`
    :   Primary reply pause duration

    `reply_count: list[int]`
    :   Reply count

    `ruleset: list[list[typing.Any]]`
    :   Ruleset

    `schedule: list[list[typing.Any]]`
    :   Schedule

    `schedule_count: list[int]`
    :   Schedule count

    `schedule_interval_type: list[str]`
    :   Schedule interval type

    `secondary_reply_action: list[str]`
    :   Secondary reply action

    `secondary_reply_pause_duration: list[int]`
    :   Secondary reply pause duration

    `sequence_states: list[list[typing.Any]]`
    :   Sequence states

    `sequence_step_count: list[int]`
    :   Sequence step count

    `sequence_steps: list[list[typing.Any]]`
    :   Sequence steps

    `sequence_type: list[str]`
    :   Sequence type

    `share_type: list[str]`
    :   Share type

    `tags: list[list[typing.Any]]`
    :   Tags

    `tasks: list[list[typing.Any]]`
    :   Tasks

    `throttle_capacity: list[int]`
    :   Throttle capacity

    `throttle_max_adds_per_day: list[int]`
    :   Throttle max adds per day

    `throttle_paused: list[bool]`
    :   Throttle paused

    `throttle_paused_at: list[str]`
    :   Throttle paused at

    `transactional: list[bool]`
    :   Transactional

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

<a id="SequencesKeywordCondition"></a>

`SequencesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.SequencesStringFilter`
    :   The type of the None singleton.

<a id="SequencesListParams"></a>

`SequencesListParams(*args, **kwargs)`
:   Parameters for sequences.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="SequencesLtCondition"></a>

`SequencesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.SequencesSearchFilter`
    :   The type of the None singleton.

<a id="SequencesLteCondition"></a>

`SequencesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.SequencesSearchFilter`
    :   The type of the None singleton.

<a id="SequencesNeqCondition"></a>

`SequencesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.SequencesSearchFilter`
    :   The type of the None singleton.

<a id="SequencesNotCondition"></a>

`SequencesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.SequencesEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesInCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesAnyCondition`
    :   The type of the None singleton.

<a id="SequencesOrCondition"></a>

`SequencesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.SequencesEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesInCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesAnyCondition]`
    :   The type of the None singleton.

<a id="SequencesSearchFilter"></a>

`SequencesSearchFilter(*args, **kwargs)`
:   Available fields for filtering sequences search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="SequencesSearchQuery"></a>

`SequencesSearchQuery(*args, **kwargs)`
:   Search query for sequences entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.SequencesEqCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesGtCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesGteCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesLtCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesLteCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesInCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesNotCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesAndCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesOrCondition | airbyte_agent_sdk.connectors.outreach.types.SequencesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.SequencesSortFilter]`
    :   The type of the None singleton.

<a id="SequencesSortFilter"></a>

`SequencesSortFilter(*args, **kwargs)`
:   Available fields for sorting sequences search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `automation_percentage: Literal['asc', 'desc']`
    :   Automation percentage

    `bounce_count: Literal['asc', 'desc']`
    :   Bounce count

    `calls: Literal['asc', 'desc']`
    :   Calls

    `click_count: Literal['asc', 'desc']`
    :   Click count

    `content_category_memberships: Literal['asc', 'desc']`
    :   Content category memberships

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `deliver_count: Literal['asc', 'desc']`
    :   Deliver count

    `description: Literal['asc', 'desc']`
    :   Description

    `duration_in_days: Literal['asc', 'desc']`
    :   Duration in days

    `enabled: Literal['asc', 'desc']`
    :   Enabled

    `enabled_at: Literal['asc', 'desc']`
    :   Enabled at

    `failure_count: Literal['asc', 'desc']`
    :   Failure count

    `finish_on_reply: Literal['asc', 'desc']`
    :   Finish on reply

    `id: Literal['asc', 'desc']`
    :   Unique sequence identifier

    `last_used_at: Literal['asc', 'desc']`
    :   Last used at

    `locked: Literal['asc', 'desc']`
    :   Locked

    `locked_at: Literal['asc', 'desc']`
    :   Locked at

    `mailings: Literal['asc', 'desc']`
    :   Mailings

    `max_activations: Literal['asc', 'desc']`
    :   Max activations

    `name: Literal['asc', 'desc']`
    :   Name

    `negative_reply_count: Literal['asc', 'desc']`
    :   Negative reply count

    `neutral_reply_count: Literal['asc', 'desc']`
    :   Neutral reply count

    `num_contacted_prospects: Literal['asc', 'desc']`
    :   Num contacted prospects

    `num_replied_prospects: Literal['asc', 'desc']`
    :   Num replied prospects

    `open_count: Literal['asc', 'desc']`
    :   Open count

    `opt_out_count: Literal['asc', 'desc']`
    :   Opt out count

    `owner: Literal['asc', 'desc']`
    :   Owner

    `positive_reply_count: Literal['asc', 'desc']`
    :   Positive reply count

    `primary_reply_action: Literal['asc', 'desc']`
    :   Primary reply action

    `primary_reply_pause_duration: Literal['asc', 'desc']`
    :   Primary reply pause duration

    `reply_count: Literal['asc', 'desc']`
    :   Reply count

    `ruleset: Literal['asc', 'desc']`
    :   Ruleset

    `schedule: Literal['asc', 'desc']`
    :   Schedule

    `schedule_count: Literal['asc', 'desc']`
    :   Schedule count

    `schedule_interval_type: Literal['asc', 'desc']`
    :   Schedule interval type

    `secondary_reply_action: Literal['asc', 'desc']`
    :   Secondary reply action

    `secondary_reply_pause_duration: Literal['asc', 'desc']`
    :   Secondary reply pause duration

    `sequence_states: Literal['asc', 'desc']`
    :   Sequence states

    `sequence_step_count: Literal['asc', 'desc']`
    :   Sequence step count

    `sequence_steps: Literal['asc', 'desc']`
    :   Sequence steps

    `sequence_type: Literal['asc', 'desc']`
    :   Sequence type

    `share_type: Literal['asc', 'desc']`
    :   Share type

    `tags: Literal['asc', 'desc']`
    :   Tags

    `tasks: Literal['asc', 'desc']`
    :   Tasks

    `throttle_capacity: Literal['asc', 'desc']`
    :   Throttle capacity

    `throttle_max_adds_per_day: Literal['asc', 'desc']`
    :   Throttle max adds per day

    `throttle_paused: Literal['asc', 'desc']`
    :   Throttle paused

    `throttle_paused_at: Literal['asc', 'desc']`
    :   Throttle paused at

    `transactional: Literal['asc', 'desc']`
    :   Transactional

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

<a id="SequencesStartswithCondition"></a>

`SequencesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.SequencesStringFilter`
    :   The type of the None singleton.

<a id="SequencesStringFilter"></a>

`SequencesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `automation_percentage: str`
    :   Automation percentage

    `bounce_count: str`
    :   Bounce count

    `calls: str`
    :   Calls

    `click_count: str`
    :   Click count

    `content_category_memberships: str`
    :   Content category memberships

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `deliver_count: str`
    :   Deliver count

    `description: str`
    :   Description

    `duration_in_days: str`
    :   Duration in days

    `enabled: str`
    :   Enabled

    `enabled_at: str`
    :   Enabled at

    `failure_count: str`
    :   Failure count

    `finish_on_reply: str`
    :   Finish on reply

    `id: str`
    :   Unique sequence identifier

    `last_used_at: str`
    :   Last used at

    `locked: str`
    :   Locked

    `locked_at: str`
    :   Locked at

    `mailings: str`
    :   Mailings

    `max_activations: str`
    :   Max activations

    `name: str`
    :   Name

    `negative_reply_count: str`
    :   Negative reply count

    `neutral_reply_count: str`
    :   Neutral reply count

    `num_contacted_prospects: str`
    :   Num contacted prospects

    `num_replied_prospects: str`
    :   Num replied prospects

    `open_count: str`
    :   Open count

    `opt_out_count: str`
    :   Opt out count

    `owner: str`
    :   Owner

    `positive_reply_count: str`
    :   Positive reply count

    `primary_reply_action: str`
    :   Primary reply action

    `primary_reply_pause_duration: str`
    :   Primary reply pause duration

    `reply_count: str`
    :   Reply count

    `ruleset: str`
    :   Ruleset

    `schedule: str`
    :   Schedule

    `schedule_count: str`
    :   Schedule count

    `schedule_interval_type: str`
    :   Schedule interval type

    `secondary_reply_action: str`
    :   Secondary reply action

    `secondary_reply_pause_duration: str`
    :   Secondary reply pause duration

    `sequence_states: str`
    :   Sequence states

    `sequence_step_count: str`
    :   Sequence step count

    `sequence_steps: str`
    :   Sequence steps

    `sequence_type: str`
    :   Sequence type

    `share_type: str`
    :   Share type

    `tags: str`
    :   Tags

    `tasks: str`
    :   Tasks

    `throttle_capacity: str`
    :   Throttle capacity

    `throttle_max_adds_per_day: str`
    :   Throttle max adds per day

    `throttle_paused: str`
    :   Throttle paused

    `throttle_paused_at: str`
    :   Throttle paused at

    `transactional: str`
    :   Transactional

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

<a id="SnippetsAndCondition"></a>

`SnippetsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.SnippetsEqCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsGtCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsGteCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsLtCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsLteCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsInCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsNotCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsAndCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsOrCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsAnyCondition]`
    :   The type of the None singleton.

<a id="SnippetsAnyCondition"></a>

`SnippetsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.SnippetsAnyValueFilter`
    :   The type of the None singleton.

<a id="SnippetsAnyValueFilter"></a>

`SnippetsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_html: Any`
    :   Body html

    `body_text: Any`
    :   Body text

    `content_category_memberships: Any`
    :   Content category memberships

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `id: Any`
    :   Unique snippet identifier

    `name: Any`
    :   Name

    `owner: Any`
    :   Owner

    `share_type: Any`
    :   Share type

    `tags: Any`
    :   Tags

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

<a id="SnippetsArrayContainsCondition"></a>

`SnippetsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.SnippetsAnyValueFilter`
    :   The type of the None singleton.

<a id="SnippetsContainsCondition"></a>

`SnippetsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.SnippetsAnyValueFilter`
    :   The type of the None singleton.

<a id="SnippetsEndswithCondition"></a>

`SnippetsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.SnippetsStringFilter`
    :   The type of the None singleton.

<a id="SnippetsEqCondition"></a>

`SnippetsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.SnippetsSearchFilter`
    :   The type of the None singleton.

<a id="SnippetsFuzzyCondition"></a>

`SnippetsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.SnippetsStringFilter`
    :   The type of the None singleton.

<a id="SnippetsGetParams"></a>

`SnippetsGetParams(*args, **kwargs)`
:   Parameters for snippets.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SnippetsGtCondition"></a>

`SnippetsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.SnippetsSearchFilter`
    :   The type of the None singleton.

<a id="SnippetsGteCondition"></a>

`SnippetsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.SnippetsSearchFilter`
    :   The type of the None singleton.

<a id="SnippetsInCondition"></a>

`SnippetsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.SnippetsInFilter`
    :   The type of the None singleton.

<a id="SnippetsInFilter"></a>

`SnippetsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_html: list[str]`
    :   Body html

    `body_text: list[str]`
    :   Body text

    `content_category_memberships: list[list[typing.Any]]`
    :   Content category memberships

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `id: list[int]`
    :   Unique snippet identifier

    `name: list[str]`
    :   Name

    `owner: list[list[typing.Any]]`
    :   Owner

    `share_type: list[str]`
    :   Share type

    `tags: list[str]`
    :   Tags

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

<a id="SnippetsKeywordCondition"></a>

`SnippetsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.SnippetsStringFilter`
    :   The type of the None singleton.

<a id="SnippetsListParams"></a>

`SnippetsListParams(*args, **kwargs)`
:   Parameters for snippets.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="SnippetsLtCondition"></a>

`SnippetsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.SnippetsSearchFilter`
    :   The type of the None singleton.

<a id="SnippetsLteCondition"></a>

`SnippetsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.SnippetsSearchFilter`
    :   The type of the None singleton.

<a id="SnippetsNeqCondition"></a>

`SnippetsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.SnippetsSearchFilter`
    :   The type of the None singleton.

<a id="SnippetsNotCondition"></a>

`SnippetsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.SnippetsEqCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsGtCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsGteCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsLtCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsLteCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsInCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsNotCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsAndCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsOrCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsAnyCondition`
    :   The type of the None singleton.

<a id="SnippetsOrCondition"></a>

`SnippetsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.SnippetsEqCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsGtCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsGteCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsLtCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsLteCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsInCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsNotCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsAndCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsOrCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsAnyCondition]`
    :   The type of the None singleton.

<a id="SnippetsSearchFilter"></a>

`SnippetsSearchFilter(*args, **kwargs)`
:   Available fields for filtering snippets search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="SnippetsSearchQuery"></a>

`SnippetsSearchQuery(*args, **kwargs)`
:   Search query for snippets entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.SnippetsEqCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsNeqCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsGtCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsGteCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsLtCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsLteCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsInCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsNotCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsAndCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsOrCondition | airbyte_agent_sdk.connectors.outreach.types.SnippetsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.SnippetsSortFilter]`
    :   The type of the None singleton.

<a id="SnippetsSortFilter"></a>

`SnippetsSortFilter(*args, **kwargs)`
:   Available fields for sorting snippets search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_html: Literal['asc', 'desc']`
    :   Body html

    `body_text: Literal['asc', 'desc']`
    :   Body text

    `content_category_memberships: Literal['asc', 'desc']`
    :   Content category memberships

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `id: Literal['asc', 'desc']`
    :   Unique snippet identifier

    `name: Literal['asc', 'desc']`
    :   Name

    `owner: Literal['asc', 'desc']`
    :   Owner

    `share_type: Literal['asc', 'desc']`
    :   Share type

    `tags: Literal['asc', 'desc']`
    :   Tags

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

<a id="SnippetsStartswithCondition"></a>

`SnippetsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.SnippetsStringFilter`
    :   The type of the None singleton.

<a id="SnippetsStringFilter"></a>

`SnippetsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_html: str`
    :   Body html

    `body_text: str`
    :   Body text

    `content_category_memberships: str`
    :   Content category memberships

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `id: str`
    :   Unique snippet identifier

    `name: str`
    :   Name

    `owner: str`
    :   Owner

    `share_type: str`
    :   Share type

    `tags: str`
    :   Tags

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

<a id="StagesAndCondition"></a>

`StagesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.StagesEqCondition | airbyte_agent_sdk.connectors.outreach.types.StagesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.StagesGtCondition | airbyte_agent_sdk.connectors.outreach.types.StagesGteCondition | airbyte_agent_sdk.connectors.outreach.types.StagesLtCondition | airbyte_agent_sdk.connectors.outreach.types.StagesLteCondition | airbyte_agent_sdk.connectors.outreach.types.StagesInCondition | airbyte_agent_sdk.connectors.outreach.types.StagesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.StagesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.StagesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.StagesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.StagesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.StagesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.StagesNotCondition | airbyte_agent_sdk.connectors.outreach.types.StagesAndCondition | airbyte_agent_sdk.connectors.outreach.types.StagesOrCondition | airbyte_agent_sdk.connectors.outreach.types.StagesAnyCondition]`
    :   The type of the None singleton.

<a id="StagesAnyCondition"></a>

`StagesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.StagesAnyValueFilter`
    :   The type of the None singleton.

<a id="StagesAnyValueFilter"></a>

`StagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Any`
    :   Color

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `id: Any`
    :   Unique stage identifier

    `name: Any`
    :   Name

    `order: Any`
    :   Order

    `prospects: Any`
    :   Prospects

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

<a id="StagesArrayContainsCondition"></a>

`StagesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.StagesAnyValueFilter`
    :   The type of the None singleton.

<a id="StagesContainsCondition"></a>

`StagesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.StagesAnyValueFilter`
    :   The type of the None singleton.

<a id="StagesEndswithCondition"></a>

`StagesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.StagesStringFilter`
    :   The type of the None singleton.

<a id="StagesEqCondition"></a>

`StagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.StagesSearchFilter`
    :   The type of the None singleton.

<a id="StagesFuzzyCondition"></a>

`StagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.StagesStringFilter`
    :   The type of the None singleton.

<a id="StagesGetParams"></a>

`StagesGetParams(*args, **kwargs)`
:   Parameters for stages.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="StagesGtCondition"></a>

`StagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.StagesSearchFilter`
    :   The type of the None singleton.

<a id="StagesGteCondition"></a>

`StagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.StagesSearchFilter`
    :   The type of the None singleton.

<a id="StagesInCondition"></a>

`StagesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.StagesInFilter`
    :   The type of the None singleton.

<a id="StagesInFilter"></a>

`StagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: list[str]`
    :   Color

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `id: list[int]`
    :   Unique stage identifier

    `name: list[str]`
    :   Name

    `order: list[int]`
    :   Order

    `prospects: list[list[typing.Any]]`
    :   Prospects

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

<a id="StagesKeywordCondition"></a>

`StagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.StagesStringFilter`
    :   The type of the None singleton.

<a id="StagesListParams"></a>

`StagesListParams(*args, **kwargs)`
:   Parameters for stages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="StagesLtCondition"></a>

`StagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.StagesSearchFilter`
    :   The type of the None singleton.

<a id="StagesLteCondition"></a>

`StagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.StagesSearchFilter`
    :   The type of the None singleton.

<a id="StagesNeqCondition"></a>

`StagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.StagesSearchFilter`
    :   The type of the None singleton.

<a id="StagesNotCondition"></a>

`StagesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.StagesEqCondition | airbyte_agent_sdk.connectors.outreach.types.StagesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.StagesGtCondition | airbyte_agent_sdk.connectors.outreach.types.StagesGteCondition | airbyte_agent_sdk.connectors.outreach.types.StagesLtCondition | airbyte_agent_sdk.connectors.outreach.types.StagesLteCondition | airbyte_agent_sdk.connectors.outreach.types.StagesInCondition | airbyte_agent_sdk.connectors.outreach.types.StagesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.StagesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.StagesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.StagesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.StagesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.StagesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.StagesNotCondition | airbyte_agent_sdk.connectors.outreach.types.StagesAndCondition | airbyte_agent_sdk.connectors.outreach.types.StagesOrCondition | airbyte_agent_sdk.connectors.outreach.types.StagesAnyCondition`
    :   The type of the None singleton.

<a id="StagesOrCondition"></a>

`StagesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.StagesEqCondition | airbyte_agent_sdk.connectors.outreach.types.StagesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.StagesGtCondition | airbyte_agent_sdk.connectors.outreach.types.StagesGteCondition | airbyte_agent_sdk.connectors.outreach.types.StagesLtCondition | airbyte_agent_sdk.connectors.outreach.types.StagesLteCondition | airbyte_agent_sdk.connectors.outreach.types.StagesInCondition | airbyte_agent_sdk.connectors.outreach.types.StagesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.StagesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.StagesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.StagesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.StagesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.StagesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.StagesNotCondition | airbyte_agent_sdk.connectors.outreach.types.StagesAndCondition | airbyte_agent_sdk.connectors.outreach.types.StagesOrCondition | airbyte_agent_sdk.connectors.outreach.types.StagesAnyCondition]`
    :   The type of the None singleton.

<a id="StagesSearchFilter"></a>

`StagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering stages search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str | None`
    :   Color

    `created_at: str | None`
    :   Created at

    `creator: list[typing.Any] | None`
    :   Creator

    `id: int | None`
    :   Unique stage identifier

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

<a id="StagesSearchQuery"></a>

`StagesSearchQuery(*args, **kwargs)`
:   Search query for stages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.StagesEqCondition | airbyte_agent_sdk.connectors.outreach.types.StagesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.StagesGtCondition | airbyte_agent_sdk.connectors.outreach.types.StagesGteCondition | airbyte_agent_sdk.connectors.outreach.types.StagesLtCondition | airbyte_agent_sdk.connectors.outreach.types.StagesLteCondition | airbyte_agent_sdk.connectors.outreach.types.StagesInCondition | airbyte_agent_sdk.connectors.outreach.types.StagesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.StagesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.StagesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.StagesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.StagesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.StagesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.StagesNotCondition | airbyte_agent_sdk.connectors.outreach.types.StagesAndCondition | airbyte_agent_sdk.connectors.outreach.types.StagesOrCondition | airbyte_agent_sdk.connectors.outreach.types.StagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.StagesSortFilter]`
    :   The type of the None singleton.

<a id="StagesSortFilter"></a>

`StagesSortFilter(*args, **kwargs)`
:   Available fields for sorting stages search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Literal['asc', 'desc']`
    :   Color

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `id: Literal['asc', 'desc']`
    :   Unique stage identifier

    `name: Literal['asc', 'desc']`
    :   Name

    `order: Literal['asc', 'desc']`
    :   Order

    `prospects: Literal['asc', 'desc']`
    :   Prospects

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

<a id="StagesStartswithCondition"></a>

`StagesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.StagesStringFilter`
    :   The type of the None singleton.

<a id="StagesStringFilter"></a>

`StagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   Color

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `id: str`
    :   Unique stage identifier

    `name: str`
    :   Name

    `order: str`
    :   Order

    `prospects: str`
    :   Prospects

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

<a id="TasksAndCondition"></a>

`TasksAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.TasksEqCondition | airbyte_agent_sdk.connectors.outreach.types.TasksNeqCondition | airbyte_agent_sdk.connectors.outreach.types.TasksGtCondition | airbyte_agent_sdk.connectors.outreach.types.TasksGteCondition | airbyte_agent_sdk.connectors.outreach.types.TasksLtCondition | airbyte_agent_sdk.connectors.outreach.types.TasksLteCondition | airbyte_agent_sdk.connectors.outreach.types.TasksInCondition | airbyte_agent_sdk.connectors.outreach.types.TasksStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.TasksEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.TasksContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TasksArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TasksNotCondition | airbyte_agent_sdk.connectors.outreach.types.TasksAndCondition | airbyte_agent_sdk.connectors.outreach.types.TasksOrCondition | airbyte_agent_sdk.connectors.outreach.types.TasksAnyCondition]`
    :   The type of the None singleton.

<a id="TasksAnyCondition"></a>

`TasksAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.TasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TasksAnyValueFilter"></a>

`TasksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Any`
    :   Account

    `action: Any`
    :   Action

    `autoskip_at: Any`
    :   Autoskip at

    `call: Any`
    :   Call

    `calls: Any`
    :   Calls

    `compiled_sequence_template_html: Any`
    :   Compiled sequence template html

    `completed: Any`
    :   Completed

    `completed_at: Any`
    :   Completed at

    `completer: Any`
    :   Completer

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `default_plugin_mapping: Any`
    :   Default plugin mapping

    `due_at: Any`
    :   Due at

    `id: Any`
    :   Unique task identifier

    `mailing: Any`
    :   Mailing

    `mailings: Any`
    :   Mailings

    `note: Any`
    :   Note

    `opportunity: Any`
    :   Opportunity

    `opportunity_association: Any`
    :   Opportunity association

    `owner: Any`
    :   Owner

    `prospect: Any`
    :   Prospect

    `prospect_account: Any`
    :   Prospect account

    `prospect_contacts: Any`
    :   Prospect contacts

    `prospect_owner: Any`
    :   Prospect owner

    `prospect_phone_numbers: Any`
    :   Prospect phone numbers

    `prospect_stage: Any`
    :   Prospect stage

    `scheduled_at: Any`
    :   Scheduled at

    `sequence: Any`
    :   Sequence

    `sequence_sequence_steps: Any`
    :   Sequence sequence steps

    `sequence_state: Any`
    :   Sequence state

    `sequence_state_sequence_step: Any`
    :   Sequence state sequence step

    `sequence_state_sequence_step_overrides: Any`
    :   Sequence state sequence step overrides

    `sequence_state_starting_template: Any`
    :   Sequence state starting template

    `sequence_step: Any`
    :   Sequence step

    `sequence_step_override_templates: Any`
    :   Sequence step override templates

    `sequence_template: Any`
    :   Sequence template

    `sequence_template_template: Any`
    :   Sequence template template

    `state: Any`
    :   State

    `state_changed_at: Any`
    :   State changed at

    `subject: Any`
    :   Subject

    `task_priority: Any`
    :   Task priority

    `task_theme: Any`
    :   Task theme

    `task_type: Any`
    :   Task type

    `template: Any`
    :   Template

    `updated_at: Any`
    :   Updated at

<a id="TasksArrayContainsCondition"></a>

`TasksArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.TasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TasksContainsCondition"></a>

`TasksContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.TasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TasksEndswithCondition"></a>

`TasksEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksEqCondition"></a>

`TasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksFuzzyCondition"></a>

`TasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksGetParams"></a>

`TasksGetParams(*args, **kwargs)`
:   Parameters for tasks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TasksGtCondition"></a>

`TasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksGteCondition"></a>

`TasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksInCondition"></a>

`TasksInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.TasksInFilter`
    :   The type of the None singleton.

<a id="TasksInFilter"></a>

`TasksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: list[list[typing.Any]]`
    :   Account

    `action: list[str]`
    :   Action

    `autoskip_at: list[str]`
    :   Autoskip at

    `call: list[list[typing.Any]]`
    :   Call

    `calls: list[list[typing.Any]]`
    :   Calls

    `compiled_sequence_template_html: list[str]`
    :   Compiled sequence template html

    `completed: list[bool]`
    :   Completed

    `completed_at: list[str]`
    :   Completed at

    `completer: list[list[typing.Any]]`
    :   Completer

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `default_plugin_mapping: list[list[typing.Any]]`
    :   Default plugin mapping

    `due_at: list[str]`
    :   Due at

    `id: list[int]`
    :   Unique task identifier

    `mailing: list[list[typing.Any]]`
    :   Mailing

    `mailings: list[list[typing.Any]]`
    :   Mailings

    `note: list[str]`
    :   Note

    `opportunity: list[list[typing.Any]]`
    :   Opportunity

    `opportunity_association: list[str]`
    :   Opportunity association

    `owner: list[list[typing.Any]]`
    :   Owner

    `prospect: list[list[typing.Any]]`
    :   Prospect

    `prospect_account: list[list[typing.Any]]`
    :   Prospect account

    `prospect_contacts: list[list[typing.Any]]`
    :   Prospect contacts

    `prospect_owner: list[list[typing.Any]]`
    :   Prospect owner

    `prospect_phone_numbers: list[list[typing.Any]]`
    :   Prospect phone numbers

    `prospect_stage: list[list[typing.Any]]`
    :   Prospect stage

    `scheduled_at: list[str]`
    :   Scheduled at

    `sequence: list[list[typing.Any]]`
    :   Sequence

    `sequence_sequence_steps: list[list[typing.Any]]`
    :   Sequence sequence steps

    `sequence_state: list[list[typing.Any]]`
    :   Sequence state

    `sequence_state_sequence_step: list[list[typing.Any]]`
    :   Sequence state sequence step

    `sequence_state_sequence_step_overrides: list[list[typing.Any]]`
    :   Sequence state sequence step overrides

    `sequence_state_starting_template: list[list[typing.Any]]`
    :   Sequence state starting template

    `sequence_step: list[list[typing.Any]]`
    :   Sequence step

    `sequence_step_override_templates: list[list[typing.Any]]`
    :   Sequence step override templates

    `sequence_template: list[list[typing.Any]]`
    :   Sequence template

    `sequence_template_template: list[list[typing.Any]]`
    :   Sequence template template

    `state: list[str]`
    :   State

    `state_changed_at: list[str]`
    :   State changed at

    `subject: list[list[typing.Any]]`
    :   Subject

    `task_priority: list[list[typing.Any]]`
    :   Task priority

    `task_theme: list[list[typing.Any]]`
    :   Task theme

    `task_type: list[str]`
    :   Task type

    `template: list[list[typing.Any]]`
    :   Template

    `updated_at: list[str]`
    :   Updated at

<a id="TasksKeywordCondition"></a>

`TasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksListParams"></a>

`TasksListParams(*args, **kwargs)`
:   Parameters for tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="TasksLtCondition"></a>

`TasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksLteCondition"></a>

`TasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksNeqCondition"></a>

`TasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksNotCondition"></a>

`TasksNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.TasksEqCondition | airbyte_agent_sdk.connectors.outreach.types.TasksNeqCondition | airbyte_agent_sdk.connectors.outreach.types.TasksGtCondition | airbyte_agent_sdk.connectors.outreach.types.TasksGteCondition | airbyte_agent_sdk.connectors.outreach.types.TasksLtCondition | airbyte_agent_sdk.connectors.outreach.types.TasksLteCondition | airbyte_agent_sdk.connectors.outreach.types.TasksInCondition | airbyte_agent_sdk.connectors.outreach.types.TasksStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.TasksEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.TasksContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TasksArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TasksNotCondition | airbyte_agent_sdk.connectors.outreach.types.TasksAndCondition | airbyte_agent_sdk.connectors.outreach.types.TasksOrCondition | airbyte_agent_sdk.connectors.outreach.types.TasksAnyCondition`
    :   The type of the None singleton.

<a id="TasksOrCondition"></a>

`TasksOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.TasksEqCondition | airbyte_agent_sdk.connectors.outreach.types.TasksNeqCondition | airbyte_agent_sdk.connectors.outreach.types.TasksGtCondition | airbyte_agent_sdk.connectors.outreach.types.TasksGteCondition | airbyte_agent_sdk.connectors.outreach.types.TasksLtCondition | airbyte_agent_sdk.connectors.outreach.types.TasksLteCondition | airbyte_agent_sdk.connectors.outreach.types.TasksInCondition | airbyte_agent_sdk.connectors.outreach.types.TasksStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.TasksEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.TasksContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TasksArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TasksNotCondition | airbyte_agent_sdk.connectors.outreach.types.TasksAndCondition | airbyte_agent_sdk.connectors.outreach.types.TasksOrCondition | airbyte_agent_sdk.connectors.outreach.types.TasksAnyCondition]`
    :   The type of the None singleton.

<a id="TasksSearchFilter"></a>

`TasksSearchFilter(*args, **kwargs)`
:   Available fields for filtering tasks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="TasksSearchQuery"></a>

`TasksSearchQuery(*args, **kwargs)`
:   Search query for tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.TasksEqCondition | airbyte_agent_sdk.connectors.outreach.types.TasksNeqCondition | airbyte_agent_sdk.connectors.outreach.types.TasksGtCondition | airbyte_agent_sdk.connectors.outreach.types.TasksGteCondition | airbyte_agent_sdk.connectors.outreach.types.TasksLtCondition | airbyte_agent_sdk.connectors.outreach.types.TasksLteCondition | airbyte_agent_sdk.connectors.outreach.types.TasksInCondition | airbyte_agent_sdk.connectors.outreach.types.TasksStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.TasksEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.TasksContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TasksArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TasksNotCondition | airbyte_agent_sdk.connectors.outreach.types.TasksAndCondition | airbyte_agent_sdk.connectors.outreach.types.TasksOrCondition | airbyte_agent_sdk.connectors.outreach.types.TasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.TasksSortFilter]`
    :   The type of the None singleton.

<a id="TasksSortFilter"></a>

`TasksSortFilter(*args, **kwargs)`
:   Available fields for sorting tasks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Literal['asc', 'desc']`
    :   Account

    `action: Literal['asc', 'desc']`
    :   Action

    `autoskip_at: Literal['asc', 'desc']`
    :   Autoskip at

    `call: Literal['asc', 'desc']`
    :   Call

    `calls: Literal['asc', 'desc']`
    :   Calls

    `compiled_sequence_template_html: Literal['asc', 'desc']`
    :   Compiled sequence template html

    `completed: Literal['asc', 'desc']`
    :   Completed

    `completed_at: Literal['asc', 'desc']`
    :   Completed at

    `completer: Literal['asc', 'desc']`
    :   Completer

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `default_plugin_mapping: Literal['asc', 'desc']`
    :   Default plugin mapping

    `due_at: Literal['asc', 'desc']`
    :   Due at

    `id: Literal['asc', 'desc']`
    :   Unique task identifier

    `mailing: Literal['asc', 'desc']`
    :   Mailing

    `mailings: Literal['asc', 'desc']`
    :   Mailings

    `note: Literal['asc', 'desc']`
    :   Note

    `opportunity: Literal['asc', 'desc']`
    :   Opportunity

    `opportunity_association: Literal['asc', 'desc']`
    :   Opportunity association

    `owner: Literal['asc', 'desc']`
    :   Owner

    `prospect: Literal['asc', 'desc']`
    :   Prospect

    `prospect_account: Literal['asc', 'desc']`
    :   Prospect account

    `prospect_contacts: Literal['asc', 'desc']`
    :   Prospect contacts

    `prospect_owner: Literal['asc', 'desc']`
    :   Prospect owner

    `prospect_phone_numbers: Literal['asc', 'desc']`
    :   Prospect phone numbers

    `prospect_stage: Literal['asc', 'desc']`
    :   Prospect stage

    `scheduled_at: Literal['asc', 'desc']`
    :   Scheduled at

    `sequence: Literal['asc', 'desc']`
    :   Sequence

    `sequence_sequence_steps: Literal['asc', 'desc']`
    :   Sequence sequence steps

    `sequence_state: Literal['asc', 'desc']`
    :   Sequence state

    `sequence_state_sequence_step: Literal['asc', 'desc']`
    :   Sequence state sequence step

    `sequence_state_sequence_step_overrides: Literal['asc', 'desc']`
    :   Sequence state sequence step overrides

    `sequence_state_starting_template: Literal['asc', 'desc']`
    :   Sequence state starting template

    `sequence_step: Literal['asc', 'desc']`
    :   Sequence step

    `sequence_step_override_templates: Literal['asc', 'desc']`
    :   Sequence step override templates

    `sequence_template: Literal['asc', 'desc']`
    :   Sequence template

    `sequence_template_template: Literal['asc', 'desc']`
    :   Sequence template template

    `state: Literal['asc', 'desc']`
    :   State

    `state_changed_at: Literal['asc', 'desc']`
    :   State changed at

    `subject: Literal['asc', 'desc']`
    :   Subject

    `task_priority: Literal['asc', 'desc']`
    :   Task priority

    `task_theme: Literal['asc', 'desc']`
    :   Task theme

    `task_type: Literal['asc', 'desc']`
    :   Task type

    `template: Literal['asc', 'desc']`
    :   Template

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

<a id="TasksStartswithCondition"></a>

`TasksStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksStringFilter"></a>

`TasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   Account

    `action: str`
    :   Action

    `autoskip_at: str`
    :   Autoskip at

    `call: str`
    :   Call

    `calls: str`
    :   Calls

    `compiled_sequence_template_html: str`
    :   Compiled sequence template html

    `completed: str`
    :   Completed

    `completed_at: str`
    :   Completed at

    `completer: str`
    :   Completer

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `default_plugin_mapping: str`
    :   Default plugin mapping

    `due_at: str`
    :   Due at

    `id: str`
    :   Unique task identifier

    `mailing: str`
    :   Mailing

    `mailings: str`
    :   Mailings

    `note: str`
    :   Note

    `opportunity: str`
    :   Opportunity

    `opportunity_association: str`
    :   Opportunity association

    `owner: str`
    :   Owner

    `prospect: str`
    :   Prospect

    `prospect_account: str`
    :   Prospect account

    `prospect_contacts: str`
    :   Prospect contacts

    `prospect_owner: str`
    :   Prospect owner

    `prospect_phone_numbers: str`
    :   Prospect phone numbers

    `prospect_stage: str`
    :   Prospect stage

    `scheduled_at: str`
    :   Scheduled at

    `sequence: str`
    :   Sequence

    `sequence_sequence_steps: str`
    :   Sequence sequence steps

    `sequence_state: str`
    :   Sequence state

    `sequence_state_sequence_step: str`
    :   Sequence state sequence step

    `sequence_state_sequence_step_overrides: str`
    :   Sequence state sequence step overrides

    `sequence_state_starting_template: str`
    :   Sequence state starting template

    `sequence_step: str`
    :   Sequence step

    `sequence_step_override_templates: str`
    :   Sequence step override templates

    `sequence_template: str`
    :   Sequence template

    `sequence_template_template: str`
    :   Sequence template template

    `state: str`
    :   State

    `state_changed_at: str`
    :   State changed at

    `subject: str`
    :   Subject

    `task_priority: str`
    :   Task priority

    `task_theme: str`
    :   Task theme

    `task_type: str`
    :   Task type

    `template: str`
    :   Template

    `updated_at: str`
    :   Updated at

<a id="TemplatesAndCondition"></a>

`TemplatesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.TemplatesEqCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesGtCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesGteCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesLtCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesLteCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesInCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesNotCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesAndCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesOrCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesAnyCondition]`
    :   The type of the None singleton.

<a id="TemplatesAnyCondition"></a>

`TemplatesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.TemplatesAnyValueFilter`
    :   The type of the None singleton.

<a id="TemplatesAnyValueFilter"></a>

`TemplatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Archived

    `archived_at: Any`
    :   Archived at

    `bcc_recipients: Any`
    :   Bcc recipients

    `body_html: Any`
    :   Body html

    `body_text: Any`
    :   Body text

    `bounce_count: Any`
    :   Bounce count

    `cc_recipients: Any`
    :   Cc recipients

    `click_count: Any`
    :   Click count

    `content_category_memberships: Any`
    :   Content category memberships

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `deliver_count: Any`
    :   Deliver count

    `failure_count: Any`
    :   Failure count

    `id: Any`
    :   Unique template identifier

    `last_used_at: Any`
    :   Last used at

    `name: Any`
    :   Name

    `negative_reply_count: Any`
    :   Negative reply count

    `neutral_reply_count: Any`
    :   Neutral reply count

    `open_count: Any`
    :   Open count

    `opt_out_count: Any`
    :   Opt out count

    `owner: Any`
    :   Owner

    `positive_reply_count: Any`
    :   Positive reply count

    `recipients: Any`
    :   Recipients

    `reply_count: Any`
    :   Reply count

    `schedule_count: Any`
    :   Schedule count

    `sequence_templates: Any`
    :   Sequence templates

    `share_type: Any`
    :   Share type

    `subject: Any`
    :   Subject

    `tags: Any`
    :   Tags

    `to_recipients: Any`
    :   To recipients

    `track_links: Any`
    :   Track links

    `track_opens: Any`
    :   Track opens

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

<a id="TemplatesArrayContainsCondition"></a>

`TemplatesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.TemplatesAnyValueFilter`
    :   The type of the None singleton.

<a id="TemplatesContainsCondition"></a>

`TemplatesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.TemplatesAnyValueFilter`
    :   The type of the None singleton.

<a id="TemplatesEndswithCondition"></a>

`TemplatesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.TemplatesStringFilter`
    :   The type of the None singleton.

<a id="TemplatesEqCondition"></a>

`TemplatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesFuzzyCondition"></a>

`TemplatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.TemplatesStringFilter`
    :   The type of the None singleton.

<a id="TemplatesGetParams"></a>

`TemplatesGetParams(*args, **kwargs)`
:   Parameters for templates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TemplatesGtCondition"></a>

`TemplatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesGteCondition"></a>

`TemplatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesInCondition"></a>

`TemplatesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.TemplatesInFilter`
    :   The type of the None singleton.

<a id="TemplatesInFilter"></a>

`TemplatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Archived

    `archived_at: list[str]`
    :   Archived at

    `bcc_recipients: list[str]`
    :   Bcc recipients

    `body_html: list[str]`
    :   Body html

    `body_text: list[str]`
    :   Body text

    `bounce_count: list[int]`
    :   Bounce count

    `cc_recipients: list[str]`
    :   Cc recipients

    `click_count: list[int]`
    :   Click count

    `content_category_memberships: list[list[typing.Any]]`
    :   Content category memberships

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `deliver_count: list[int]`
    :   Deliver count

    `failure_count: list[int]`
    :   Failure count

    `id: list[int]`
    :   Unique template identifier

    `last_used_at: list[str]`
    :   Last used at

    `name: list[str]`
    :   Name

    `negative_reply_count: list[int]`
    :   Negative reply count

    `neutral_reply_count: list[int]`
    :   Neutral reply count

    `open_count: list[int]`
    :   Open count

    `opt_out_count: list[int]`
    :   Opt out count

    `owner: list[list[typing.Any]]`
    :   Owner

    `positive_reply_count: list[int]`
    :   Positive reply count

    `recipients: list[list[typing.Any]]`
    :   Recipients

    `reply_count: list[int]`
    :   Reply count

    `schedule_count: list[int]`
    :   Schedule count

    `sequence_templates: list[list[typing.Any]]`
    :   Sequence templates

    `share_type: list[str]`
    :   Share type

    `subject: list[str]`
    :   Subject

    `tags: list[str]`
    :   Tags

    `to_recipients: list[str]`
    :   To recipients

    `track_links: list[bool]`
    :   Track links

    `track_opens: list[bool]`
    :   Track opens

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

<a id="TemplatesKeywordCondition"></a>

`TemplatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.TemplatesStringFilter`
    :   The type of the None singleton.

<a id="TemplatesListParams"></a>

`TemplatesListParams(*args, **kwargs)`
:   Parameters for templates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="TemplatesLtCondition"></a>

`TemplatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesLteCondition"></a>

`TemplatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesNeqCondition"></a>

`TemplatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesNotCondition"></a>

`TemplatesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.TemplatesEqCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesGtCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesGteCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesLtCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesLteCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesInCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesNotCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesAndCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesOrCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesAnyCondition`
    :   The type of the None singleton.

<a id="TemplatesOrCondition"></a>

`TemplatesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.TemplatesEqCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesGtCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesGteCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesLtCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesLteCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesInCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesNotCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesAndCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesOrCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesAnyCondition]`
    :   The type of the None singleton.

<a id="TemplatesSearchFilter"></a>

`TemplatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering templates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="TemplatesSearchQuery"></a>

`TemplatesSearchQuery(*args, **kwargs)`
:   Search query for templates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.TemplatesEqCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesNeqCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesGtCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesGteCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesLtCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesLteCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesInCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesNotCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesAndCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesOrCondition | airbyte_agent_sdk.connectors.outreach.types.TemplatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.TemplatesSortFilter]`
    :   The type of the None singleton.

<a id="TemplatesSortFilter"></a>

`TemplatesSortFilter(*args, **kwargs)`
:   Available fields for sorting templates search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Archived

    `archived_at: Literal['asc', 'desc']`
    :   Archived at

    `bcc_recipients: Literal['asc', 'desc']`
    :   Bcc recipients

    `body_html: Literal['asc', 'desc']`
    :   Body html

    `body_text: Literal['asc', 'desc']`
    :   Body text

    `bounce_count: Literal['asc', 'desc']`
    :   Bounce count

    `cc_recipients: Literal['asc', 'desc']`
    :   Cc recipients

    `click_count: Literal['asc', 'desc']`
    :   Click count

    `content_category_memberships: Literal['asc', 'desc']`
    :   Content category memberships

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `deliver_count: Literal['asc', 'desc']`
    :   Deliver count

    `failure_count: Literal['asc', 'desc']`
    :   Failure count

    `id: Literal['asc', 'desc']`
    :   Unique template identifier

    `last_used_at: Literal['asc', 'desc']`
    :   Last used at

    `name: Literal['asc', 'desc']`
    :   Name

    `negative_reply_count: Literal['asc', 'desc']`
    :   Negative reply count

    `neutral_reply_count: Literal['asc', 'desc']`
    :   Neutral reply count

    `open_count: Literal['asc', 'desc']`
    :   Open count

    `opt_out_count: Literal['asc', 'desc']`
    :   Opt out count

    `owner: Literal['asc', 'desc']`
    :   Owner

    `positive_reply_count: Literal['asc', 'desc']`
    :   Positive reply count

    `recipients: Literal['asc', 'desc']`
    :   Recipients

    `reply_count: Literal['asc', 'desc']`
    :   Reply count

    `schedule_count: Literal['asc', 'desc']`
    :   Schedule count

    `sequence_templates: Literal['asc', 'desc']`
    :   Sequence templates

    `share_type: Literal['asc', 'desc']`
    :   Share type

    `subject: Literal['asc', 'desc']`
    :   Subject

    `tags: Literal['asc', 'desc']`
    :   Tags

    `to_recipients: Literal['asc', 'desc']`
    :   To recipients

    `track_links: Literal['asc', 'desc']`
    :   Track links

    `track_opens: Literal['asc', 'desc']`
    :   Track opens

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

<a id="TemplatesStartswithCondition"></a>

`TemplatesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.TemplatesStringFilter`
    :   The type of the None singleton.

<a id="TemplatesStringFilter"></a>

`TemplatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Archived

    `archived_at: str`
    :   Archived at

    `bcc_recipients: str`
    :   Bcc recipients

    `body_html: str`
    :   Body html

    `body_text: str`
    :   Body text

    `bounce_count: str`
    :   Bounce count

    `cc_recipients: str`
    :   Cc recipients

    `click_count: str`
    :   Click count

    `content_category_memberships: str`
    :   Content category memberships

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `deliver_count: str`
    :   Deliver count

    `failure_count: str`
    :   Failure count

    `id: str`
    :   Unique template identifier

    `last_used_at: str`
    :   Last used at

    `name: str`
    :   Name

    `negative_reply_count: str`
    :   Negative reply count

    `neutral_reply_count: str`
    :   Neutral reply count

    `open_count: str`
    :   Open count

    `opt_out_count: str`
    :   Opt out count

    `owner: str`
    :   Owner

    `positive_reply_count: str`
    :   Positive reply count

    `recipients: str`
    :   Recipients

    `reply_count: str`
    :   Reply count

    `schedule_count: str`
    :   Schedule count

    `sequence_templates: str`
    :   Sequence templates

    `share_type: str`
    :   Share type

    `subject: str`
    :   Subject

    `tags: str`
    :   Tags

    `to_recipients: str`
    :   To recipients

    `track_links: str`
    :   Track links

    `track_opens: str`
    :   Track opens

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

<a id="UsersAndCondition"></a>

`UsersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.outreach.types.UsersEqCondition | airbyte_agent_sdk.connectors.outreach.types.UsersNeqCondition | airbyte_agent_sdk.connectors.outreach.types.UsersGtCondition | airbyte_agent_sdk.connectors.outreach.types.UsersGteCondition | airbyte_agent_sdk.connectors.outreach.types.UsersLtCondition | airbyte_agent_sdk.connectors.outreach.types.UsersLteCondition | airbyte_agent_sdk.connectors.outreach.types.UsersInCondition | airbyte_agent_sdk.connectors.outreach.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.UsersContainsCondition | airbyte_agent_sdk.connectors.outreach.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.UsersNotCondition | airbyte_agent_sdk.connectors.outreach.types.UsersAndCondition | airbyte_agent_sdk.connectors.outreach.types.UsersOrCondition | airbyte_agent_sdk.connectors.outreach.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersAnyCondition"></a>

`UsersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.outreach.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accounts_view_id: Any`
    :   Accounts view id

    `active_prospects_count: Any`
    :   Active prospects count

    `activity_notifications_disabled: Any`
    :   Activity notifications disabled

    `batches: Any`
    :   Batches

    `batches_view_id: Any`
    :   Batches view id

    `bounce_warning_email_enabled: Any`
    :   Bounce warning email enabled

    `bridge_phone: Any`
    :   Bridge phone

    `bridge_phone_extension: Any`
    :   Bridge phone extension

    `buyer_language_preference: Any`
    :   Buyer language preference

    `calendar: Any`
    :   Calendar

    `calendar_events_view_id: Any`
    :   Calendar events view id

    `calls_view_id: Any`
    :   Calls view id

    `content_categories: Any`
    :   Content categories

    `content_category_ownerships: Any`
    :   Content category ownerships

    `controlled_tab_default: Any`
    :   Controlled tab default

    `created_at: Any`
    :   Created at

    `creator: Any`
    :   Creator

    `current_sign_in_at: Any`
    :   Current sign in at

    `custom1: Any`
    :   Custom field 1

    `custom2: Any`
    :   Custom field 2

    `custom3: Any`
    :   Custom field 3

    `custom4: Any`
    :   Custom field 4

    `custom5: Any`
    :   Custom field 5

    `daily_digest_email_enabled: Any`
    :   Daily digest email enabled

    `default_ruleset_id: Any`
    :   Default ruleset id

    `default_schedule_id: Any`
    :   Default schedule id

    `duties: Any`
    :   Duties

    `duties_set_at: Any`
    :   Duties set at

    `email: Any`
    :   Email

    `enable_voice_recordings: Any`
    :   Enable voice recordings

    `engagement_emails_enabled: Any`
    :   Engagement emails enabled

    `favorites: Any`
    :   Favorites

    `first_name: Any`
    :   First name

    `global_id: Any`
    :   Global id

    `id: Any`
    :   Unique user identifier

    `imports_view_id: Any`
    :   Imports view id

    `inbound_bridge_phone: Any`
    :   Inbound bridge phone

    `inbound_bridge_phone_extension: Any`
    :   Inbound bridge phone extension

    `inbound_call_behavior: Any`
    :   Inbound call behavior

    `inbound_phone_type: Any`
    :   Inbound phone type

    `inbound_voicemail_custom_message_text: Any`
    :   Inbound voicemail custom message text

    `inbound_voicemail_message_text_voice: Any`
    :   Inbound voicemail message text voice

    `inbound_voicemail_prompt_type: Any`
    :   Inbound voicemail prompt type

    `job_role: Any`
    :   Job role

    `kaia_recordings_view_id: Any`
    :   Kaia recordings view id

    `keep_bridge_phone_connected: Any`
    :   Keep bridge phone connected

    `language_preference: Any`
    :   Language preference

    `last_name: Any`
    :   Last name

    `last_sign_in_at: Any`
    :   Last sign in at

    `link_to_sequence_state_in_task_flow: Any`
    :   Link to sequence state in task flow

    `live_listen_view_id: Any`
    :   Live listen view id

    `locked: Any`
    :   Locked

    `mailbox: Any`
    :   Mailbox

    `mailbox_error_email_enabled: Any`
    :   Mailbox error email enabled

    `mailboxes: Any`
    :   Mailboxes

    `mailings_delivered_count: Any`
    :   Mailings delivered count

    `mailings_replied_count: Any`
    :   Mailings replied count

    `mailings_view_id: Any`
    :   Mailings view id

    `meeting_engagement_notification_enabled: Any`
    :   Meeting engagement notification enabled

    `meeting_types_view_id: Any`
    :   Meeting types view id

    `name: Any`
    :   Name

    `notifications_enabled: Any`
    :   Notifications enabled

    `oce_click_to_dial_everywhere: Any`
    :   Oce click to dial everywhere

    `oce_gmail_toolbar: Any`
    :   Oce gmail toolbar

    `oce_gmail_tracking_state: Any`
    :   Oce gmail tracking state

    `oce_salesforce_email_decorating: Any`
    :   Oce salesforce email decorating

    `oce_salesforce_phone_decorating: Any`
    :   Oce salesforce phone decorating

    `oce_universal_task_flow: Any`
    :   Oce universal task flow

    `oce_window_mode: Any`
    :   Oce window mode

    `onboarded_at: Any`
    :   Onboarded at

    `opportunities_view_id: Any`
    :   Opportunities view id

    `orca_standalone_enabled: Any`
    :   Orca standalone enabled

    `outbound_voicemails: Any`
    :   Outbound voicemails

    `password_expires_at: Any`
    :   Password expires at

    `phone: Any`
    :   Phone

    `phone_country_code: Any`
    :   Phone country code

    `phone_number: Any`
    :   Phone number

    `phone_type: Any`
    :   Phone type

    `phones: Any`
    :   Phones

    `phones_view_id: Any`
    :   Phones view id

    `plugin_alert_notification_enabled: Any`
    :   Plugin alert notification enabled

    `preferred_voice_region: Any`
    :   Preferred voice region

    `prefers_local_presence: Any`
    :   Prefers local presence

    `primary_timezone: Any`
    :   Primary timezone

    `profile: Any`
    :   Profile

    `prospect_detail_default: Any`
    :   Prospect detail default

    `prospects_view_id: Any`
    :   Prospects view id

    `recipients: Any`
    :   Recipients

    `reports_sequence_performance_view_id: Any`
    :   Reports sequence performance view id

    `reports_team_perf_view_id: Any`
    :   Reports team perf view id

    `reports_team_performance_intraday_view_id: Any`
    :   Reports team performance intraday view id

    `reports_team_performance_view_id: Any`
    :   Reports team performance view id

    `reports_view_id: Any`
    :   Reports view id

    `role: Any`
    :   Role

    `scim_external_id: Any`
    :   Scim external id

    `scim_source: Any`
    :   Scim source

    `secondary_timezone: Any`
    :   Secondary timezone

    `send_invite_fallback: Any`
    :   Send invite fallback

    `sender_notifications_excluded: Any`
    :   Sender notifications excluded

    `sequence_states_view_id: Any`
    :   Sequence states view id

    `sequences_view_id: Any`
    :   Sequences view id

    `sms_phone: Any`
    :   Sms phone

    `snippets_view_id: Any`
    :   Snippets view id

    `tasks_due_count: Any`
    :   Tasks due count

    `tasks_view_id: Any`
    :   Tasks view id

    `teams: Any`
    :   Teams

    `teams_view_id: Any`
    :   Teams view id

    `templates_view_id: Any`
    :   Templates view id

    `tertiary_timezone: Any`
    :   Tertiary timezone

    `texting_email_notifications: Any`
    :   Texting email notifications

    `title: Any`
    :   Title

    `unknown_reply_email_enabled: Any`
    :   Unknown reply email enabled

    `updated_at: Any`
    :   Updated at

    `updater: Any`
    :   Updater

    `use_sales_navigator_for_linked_in_tasks: Any`
    :   Use sales navigator for linked in tasks

    `user_guid: Any`
    :   User guid

    `username: Any`
    :   Username

    `users_view_id: Any`
    :   Users view id

    `voicemail_notification_enabled: Any`
    :   Voicemail notification enabled

    `voicemail_prompts: Any`
    :   Voicemail prompts

    `weekly_digest_email_enabled: Any`
    :   Weekly digest email enabled

<a id="UsersArrayContainsCondition"></a>

`UsersArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.outreach.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.outreach.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEndswithCondition"></a>

`UsersEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.outreach.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.outreach.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.outreach.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="UsersGtCondition"></a>

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.outreach.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.outreach.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersInCondition"></a>

`UsersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.outreach.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accounts_view_id: list[int]`
    :   Accounts view id

    `active_prospects_count: list[int]`
    :   Active prospects count

    `activity_notifications_disabled: list[bool]`
    :   Activity notifications disabled

    `batches: list[list[typing.Any]]`
    :   Batches

    `batches_view_id: list[int]`
    :   Batches view id

    `bounce_warning_email_enabled: list[bool]`
    :   Bounce warning email enabled

    `bridge_phone: list[str]`
    :   Bridge phone

    `bridge_phone_extension: list[str]`
    :   Bridge phone extension

    `buyer_language_preference: list[str]`
    :   Buyer language preference

    `calendar: list[list[typing.Any]]`
    :   Calendar

    `calendar_events_view_id: list[int]`
    :   Calendar events view id

    `calls_view_id: list[int]`
    :   Calls view id

    `content_categories: list[list[typing.Any]]`
    :   Content categories

    `content_category_ownerships: list[list[typing.Any]]`
    :   Content category ownerships

    `controlled_tab_default: list[str]`
    :   Controlled tab default

    `created_at: list[str]`
    :   Created at

    `creator: list[list[typing.Any]]`
    :   Creator

    `current_sign_in_at: list[str]`
    :   Current sign in at

    `custom1: list[str]`
    :   Custom field 1

    `custom2: list[str]`
    :   Custom field 2

    `custom3: list[str]`
    :   Custom field 3

    `custom4: list[str]`
    :   Custom field 4

    `custom5: list[str]`
    :   Custom field 5

    `daily_digest_email_enabled: list[bool]`
    :   Daily digest email enabled

    `default_ruleset_id: list[int]`
    :   Default ruleset id

    `default_schedule_id: list[int]`
    :   Default schedule id

    `duties: list[list[typing.Any]]`
    :   Duties

    `duties_set_at: list[str]`
    :   Duties set at

    `email: list[str]`
    :   Email

    `enable_voice_recordings: list[bool]`
    :   Enable voice recordings

    `engagement_emails_enabled: list[bool]`
    :   Engagement emails enabled

    `favorites: list[list[typing.Any]]`
    :   Favorites

    `first_name: list[str]`
    :   First name

    `global_id: list[str]`
    :   Global id

    `id: list[int]`
    :   Unique user identifier

    `imports_view_id: list[int]`
    :   Imports view id

    `inbound_bridge_phone: list[str]`
    :   Inbound bridge phone

    `inbound_bridge_phone_extension: list[str]`
    :   Inbound bridge phone extension

    `inbound_call_behavior: list[str]`
    :   Inbound call behavior

    `inbound_phone_type: list[str]`
    :   Inbound phone type

    `inbound_voicemail_custom_message_text: list[str]`
    :   Inbound voicemail custom message text

    `inbound_voicemail_message_text_voice: list[str]`
    :   Inbound voicemail message text voice

    `inbound_voicemail_prompt_type: list[str]`
    :   Inbound voicemail prompt type

    `job_role: list[list[typing.Any]]`
    :   Job role

    `kaia_recordings_view_id: list[int]`
    :   Kaia recordings view id

    `keep_bridge_phone_connected: list[bool]`
    :   Keep bridge phone connected

    `language_preference: list[str]`
    :   Language preference

    `last_name: list[str]`
    :   Last name

    `last_sign_in_at: list[str]`
    :   Last sign in at

    `link_to_sequence_state_in_task_flow: list[bool]`
    :   Link to sequence state in task flow

    `live_listen_view_id: list[int]`
    :   Live listen view id

    `locked: list[bool]`
    :   Locked

    `mailbox: list[list[typing.Any]]`
    :   Mailbox

    `mailbox_error_email_enabled: list[bool]`
    :   Mailbox error email enabled

    `mailboxes: list[list[typing.Any]]`
    :   Mailboxes

    `mailings_delivered_count: list[int]`
    :   Mailings delivered count

    `mailings_replied_count: list[int]`
    :   Mailings replied count

    `mailings_view_id: list[int]`
    :   Mailings view id

    `meeting_engagement_notification_enabled: list[bool]`
    :   Meeting engagement notification enabled

    `meeting_types_view_id: list[int]`
    :   Meeting types view id

    `name: list[str]`
    :   Name

    `notifications_enabled: list[bool]`
    :   Notifications enabled

    `oce_click_to_dial_everywhere: list[bool]`
    :   Oce click to dial everywhere

    `oce_gmail_toolbar: list[bool]`
    :   Oce gmail toolbar

    `oce_gmail_tracking_state: list[str]`
    :   Oce gmail tracking state

    `oce_salesforce_email_decorating: list[bool]`
    :   Oce salesforce email decorating

    `oce_salesforce_phone_decorating: list[bool]`
    :   Oce salesforce phone decorating

    `oce_universal_task_flow: list[bool]`
    :   Oce universal task flow

    `oce_window_mode: list[bool]`
    :   Oce window mode

    `onboarded_at: list[str]`
    :   Onboarded at

    `opportunities_view_id: list[int]`
    :   Opportunities view id

    `orca_standalone_enabled: list[bool]`
    :   Orca standalone enabled

    `outbound_voicemails: list[list[typing.Any]]`
    :   Outbound voicemails

    `password_expires_at: list[str]`
    :   Password expires at

    `phone: list[list[typing.Any]]`
    :   Phone

    `phone_country_code: list[str]`
    :   Phone country code

    `phone_number: list[str]`
    :   Phone number

    `phone_type: list[str]`
    :   Phone type

    `phones: list[list[typing.Any]]`
    :   Phones

    `phones_view_id: list[int]`
    :   Phones view id

    `plugin_alert_notification_enabled: list[bool]`
    :   Plugin alert notification enabled

    `preferred_voice_region: list[str]`
    :   Preferred voice region

    `prefers_local_presence: list[bool]`
    :   Prefers local presence

    `primary_timezone: list[str]`
    :   Primary timezone

    `profile: list[list[typing.Any]]`
    :   Profile

    `prospect_detail_default: list[str]`
    :   Prospect detail default

    `prospects_view_id: list[int]`
    :   Prospects view id

    `recipients: list[list[typing.Any]]`
    :   Recipients

    `reports_sequence_performance_view_id: list[int]`
    :   Reports sequence performance view id

    `reports_team_perf_view_id: list[int]`
    :   Reports team perf view id

    `reports_team_performance_intraday_view_id: list[int]`
    :   Reports team performance intraday view id

    `reports_team_performance_view_id: list[int]`
    :   Reports team performance view id

    `reports_view_id: list[int]`
    :   Reports view id

    `role: list[list[typing.Any]]`
    :   Role

    `scim_external_id: list[str]`
    :   Scim external id

    `scim_source: list[str]`
    :   Scim source

    `secondary_timezone: list[str]`
    :   Secondary timezone

    `send_invite_fallback: list[bool]`
    :   Send invite fallback

    `sender_notifications_excluded: list[bool]`
    :   Sender notifications excluded

    `sequence_states_view_id: list[int]`
    :   Sequence states view id

    `sequences_view_id: list[int]`
    :   Sequences view id

    `sms_phone: list[list[typing.Any]]`
    :   Sms phone

    `snippets_view_id: list[int]`
    :   Snippets view id

    `tasks_due_count: list[int]`
    :   Tasks due count

    `tasks_view_id: list[int]`
    :   Tasks view id

    `teams: list[list[typing.Any]]`
    :   Teams

    `teams_view_id: list[int]`
    :   Teams view id

    `templates_view_id: list[int]`
    :   Templates view id

    `tertiary_timezone: list[str]`
    :   Tertiary timezone

    `texting_email_notifications: list[bool]`
    :   Texting email notifications

    `title: list[str]`
    :   Title

    `unknown_reply_email_enabled: list[bool]`
    :   Unknown reply email enabled

    `updated_at: list[str]`
    :   Updated at

    `updater: list[list[typing.Any]]`
    :   Updater

    `use_sales_navigator_for_linked_in_tasks: list[bool]`
    :   Use sales navigator for linked in tasks

    `user_guid: list[str]`
    :   User guid

    `username: list[str]`
    :   Username

    `users_view_id: list[int]`
    :   Users view id

    `voicemail_notification_enabled: list[bool]`
    :   Voicemail notification enabled

    `voicemail_prompts: list[list[typing.Any]]`
    :   Voicemail prompts

    `weekly_digest_email_enabled: list[bool]`
    :   Weekly digest email enabled

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.outreach.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The type of the None singleton.

    `page_after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.outreach.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.outreach.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.outreach.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNotCondition"></a>

`UsersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.outreach.types.UsersEqCondition | airbyte_agent_sdk.connectors.outreach.types.UsersNeqCondition | airbyte_agent_sdk.connectors.outreach.types.UsersGtCondition | airbyte_agent_sdk.connectors.outreach.types.UsersGteCondition | airbyte_agent_sdk.connectors.outreach.types.UsersLtCondition | airbyte_agent_sdk.connectors.outreach.types.UsersLteCondition | airbyte_agent_sdk.connectors.outreach.types.UsersInCondition | airbyte_agent_sdk.connectors.outreach.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.UsersContainsCondition | airbyte_agent_sdk.connectors.outreach.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.UsersNotCondition | airbyte_agent_sdk.connectors.outreach.types.UsersAndCondition | airbyte_agent_sdk.connectors.outreach.types.UsersOrCondition | airbyte_agent_sdk.connectors.outreach.types.UsersAnyCondition`
    :   The type of the None singleton.

<a id="UsersOrCondition"></a>

`UsersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.outreach.types.UsersEqCondition | airbyte_agent_sdk.connectors.outreach.types.UsersNeqCondition | airbyte_agent_sdk.connectors.outreach.types.UsersGtCondition | airbyte_agent_sdk.connectors.outreach.types.UsersGteCondition | airbyte_agent_sdk.connectors.outreach.types.UsersLtCondition | airbyte_agent_sdk.connectors.outreach.types.UsersLteCondition | airbyte_agent_sdk.connectors.outreach.types.UsersInCondition | airbyte_agent_sdk.connectors.outreach.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.UsersContainsCondition | airbyte_agent_sdk.connectors.outreach.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.UsersNotCondition | airbyte_agent_sdk.connectors.outreach.types.UsersAndCondition | airbyte_agent_sdk.connectors.outreach.types.UsersOrCondition | airbyte_agent_sdk.connectors.outreach.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.outreach.types.UsersEqCondition | airbyte_agent_sdk.connectors.outreach.types.UsersNeqCondition | airbyte_agent_sdk.connectors.outreach.types.UsersGtCondition | airbyte_agent_sdk.connectors.outreach.types.UsersGteCondition | airbyte_agent_sdk.connectors.outreach.types.UsersLtCondition | airbyte_agent_sdk.connectors.outreach.types.UsersLteCondition | airbyte_agent_sdk.connectors.outreach.types.UsersInCondition | airbyte_agent_sdk.connectors.outreach.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.outreach.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.outreach.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.outreach.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.outreach.types.UsersContainsCondition | airbyte_agent_sdk.connectors.outreach.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.outreach.types.UsersNotCondition | airbyte_agent_sdk.connectors.outreach.types.UsersAndCondition | airbyte_agent_sdk.connectors.outreach.types.UsersOrCondition | airbyte_agent_sdk.connectors.outreach.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.outreach.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accounts_view_id: Literal['asc', 'desc']`
    :   Accounts view id

    `active_prospects_count: Literal['asc', 'desc']`
    :   Active prospects count

    `activity_notifications_disabled: Literal['asc', 'desc']`
    :   Activity notifications disabled

    `batches: Literal['asc', 'desc']`
    :   Batches

    `batches_view_id: Literal['asc', 'desc']`
    :   Batches view id

    `bounce_warning_email_enabled: Literal['asc', 'desc']`
    :   Bounce warning email enabled

    `bridge_phone: Literal['asc', 'desc']`
    :   Bridge phone

    `bridge_phone_extension: Literal['asc', 'desc']`
    :   Bridge phone extension

    `buyer_language_preference: Literal['asc', 'desc']`
    :   Buyer language preference

    `calendar: Literal['asc', 'desc']`
    :   Calendar

    `calendar_events_view_id: Literal['asc', 'desc']`
    :   Calendar events view id

    `calls_view_id: Literal['asc', 'desc']`
    :   Calls view id

    `content_categories: Literal['asc', 'desc']`
    :   Content categories

    `content_category_ownerships: Literal['asc', 'desc']`
    :   Content category ownerships

    `controlled_tab_default: Literal['asc', 'desc']`
    :   Controlled tab default

    `created_at: Literal['asc', 'desc']`
    :   Created at

    `creator: Literal['asc', 'desc']`
    :   Creator

    `current_sign_in_at: Literal['asc', 'desc']`
    :   Current sign in at

    `custom1: Literal['asc', 'desc']`
    :   Custom field 1

    `custom2: Literal['asc', 'desc']`
    :   Custom field 2

    `custom3: Literal['asc', 'desc']`
    :   Custom field 3

    `custom4: Literal['asc', 'desc']`
    :   Custom field 4

    `custom5: Literal['asc', 'desc']`
    :   Custom field 5

    `daily_digest_email_enabled: Literal['asc', 'desc']`
    :   Daily digest email enabled

    `default_ruleset_id: Literal['asc', 'desc']`
    :   Default ruleset id

    `default_schedule_id: Literal['asc', 'desc']`
    :   Default schedule id

    `duties: Literal['asc', 'desc']`
    :   Duties

    `duties_set_at: Literal['asc', 'desc']`
    :   Duties set at

    `email: Literal['asc', 'desc']`
    :   Email

    `enable_voice_recordings: Literal['asc', 'desc']`
    :   Enable voice recordings

    `engagement_emails_enabled: Literal['asc', 'desc']`
    :   Engagement emails enabled

    `favorites: Literal['asc', 'desc']`
    :   Favorites

    `first_name: Literal['asc', 'desc']`
    :   First name

    `global_id: Literal['asc', 'desc']`
    :   Global id

    `id: Literal['asc', 'desc']`
    :   Unique user identifier

    `imports_view_id: Literal['asc', 'desc']`
    :   Imports view id

    `inbound_bridge_phone: Literal['asc', 'desc']`
    :   Inbound bridge phone

    `inbound_bridge_phone_extension: Literal['asc', 'desc']`
    :   Inbound bridge phone extension

    `inbound_call_behavior: Literal['asc', 'desc']`
    :   Inbound call behavior

    `inbound_phone_type: Literal['asc', 'desc']`
    :   Inbound phone type

    `inbound_voicemail_custom_message_text: Literal['asc', 'desc']`
    :   Inbound voicemail custom message text

    `inbound_voicemail_message_text_voice: Literal['asc', 'desc']`
    :   Inbound voicemail message text voice

    `inbound_voicemail_prompt_type: Literal['asc', 'desc']`
    :   Inbound voicemail prompt type

    `job_role: Literal['asc', 'desc']`
    :   Job role

    `kaia_recordings_view_id: Literal['asc', 'desc']`
    :   Kaia recordings view id

    `keep_bridge_phone_connected: Literal['asc', 'desc']`
    :   Keep bridge phone connected

    `language_preference: Literal['asc', 'desc']`
    :   Language preference

    `last_name: Literal['asc', 'desc']`
    :   Last name

    `last_sign_in_at: Literal['asc', 'desc']`
    :   Last sign in at

    `link_to_sequence_state_in_task_flow: Literal['asc', 'desc']`
    :   Link to sequence state in task flow

    `live_listen_view_id: Literal['asc', 'desc']`
    :   Live listen view id

    `locked: Literal['asc', 'desc']`
    :   Locked

    `mailbox: Literal['asc', 'desc']`
    :   Mailbox

    `mailbox_error_email_enabled: Literal['asc', 'desc']`
    :   Mailbox error email enabled

    `mailboxes: Literal['asc', 'desc']`
    :   Mailboxes

    `mailings_delivered_count: Literal['asc', 'desc']`
    :   Mailings delivered count

    `mailings_replied_count: Literal['asc', 'desc']`
    :   Mailings replied count

    `mailings_view_id: Literal['asc', 'desc']`
    :   Mailings view id

    `meeting_engagement_notification_enabled: Literal['asc', 'desc']`
    :   Meeting engagement notification enabled

    `meeting_types_view_id: Literal['asc', 'desc']`
    :   Meeting types view id

    `name: Literal['asc', 'desc']`
    :   Name

    `notifications_enabled: Literal['asc', 'desc']`
    :   Notifications enabled

    `oce_click_to_dial_everywhere: Literal['asc', 'desc']`
    :   Oce click to dial everywhere

    `oce_gmail_toolbar: Literal['asc', 'desc']`
    :   Oce gmail toolbar

    `oce_gmail_tracking_state: Literal['asc', 'desc']`
    :   Oce gmail tracking state

    `oce_salesforce_email_decorating: Literal['asc', 'desc']`
    :   Oce salesforce email decorating

    `oce_salesforce_phone_decorating: Literal['asc', 'desc']`
    :   Oce salesforce phone decorating

    `oce_universal_task_flow: Literal['asc', 'desc']`
    :   Oce universal task flow

    `oce_window_mode: Literal['asc', 'desc']`
    :   Oce window mode

    `onboarded_at: Literal['asc', 'desc']`
    :   Onboarded at

    `opportunities_view_id: Literal['asc', 'desc']`
    :   Opportunities view id

    `orca_standalone_enabled: Literal['asc', 'desc']`
    :   Orca standalone enabled

    `outbound_voicemails: Literal['asc', 'desc']`
    :   Outbound voicemails

    `password_expires_at: Literal['asc', 'desc']`
    :   Password expires at

    `phone: Literal['asc', 'desc']`
    :   Phone

    `phone_country_code: Literal['asc', 'desc']`
    :   Phone country code

    `phone_number: Literal['asc', 'desc']`
    :   Phone number

    `phone_type: Literal['asc', 'desc']`
    :   Phone type

    `phones: Literal['asc', 'desc']`
    :   Phones

    `phones_view_id: Literal['asc', 'desc']`
    :   Phones view id

    `plugin_alert_notification_enabled: Literal['asc', 'desc']`
    :   Plugin alert notification enabled

    `preferred_voice_region: Literal['asc', 'desc']`
    :   Preferred voice region

    `prefers_local_presence: Literal['asc', 'desc']`
    :   Prefers local presence

    `primary_timezone: Literal['asc', 'desc']`
    :   Primary timezone

    `profile: Literal['asc', 'desc']`
    :   Profile

    `prospect_detail_default: Literal['asc', 'desc']`
    :   Prospect detail default

    `prospects_view_id: Literal['asc', 'desc']`
    :   Prospects view id

    `recipients: Literal['asc', 'desc']`
    :   Recipients

    `reports_sequence_performance_view_id: Literal['asc', 'desc']`
    :   Reports sequence performance view id

    `reports_team_perf_view_id: Literal['asc', 'desc']`
    :   Reports team perf view id

    `reports_team_performance_intraday_view_id: Literal['asc', 'desc']`
    :   Reports team performance intraday view id

    `reports_team_performance_view_id: Literal['asc', 'desc']`
    :   Reports team performance view id

    `reports_view_id: Literal['asc', 'desc']`
    :   Reports view id

    `role: Literal['asc', 'desc']`
    :   Role

    `scim_external_id: Literal['asc', 'desc']`
    :   Scim external id

    `scim_source: Literal['asc', 'desc']`
    :   Scim source

    `secondary_timezone: Literal['asc', 'desc']`
    :   Secondary timezone

    `send_invite_fallback: Literal['asc', 'desc']`
    :   Send invite fallback

    `sender_notifications_excluded: Literal['asc', 'desc']`
    :   Sender notifications excluded

    `sequence_states_view_id: Literal['asc', 'desc']`
    :   Sequence states view id

    `sequences_view_id: Literal['asc', 'desc']`
    :   Sequences view id

    `sms_phone: Literal['asc', 'desc']`
    :   Sms phone

    `snippets_view_id: Literal['asc', 'desc']`
    :   Snippets view id

    `tasks_due_count: Literal['asc', 'desc']`
    :   Tasks due count

    `tasks_view_id: Literal['asc', 'desc']`
    :   Tasks view id

    `teams: Literal['asc', 'desc']`
    :   Teams

    `teams_view_id: Literal['asc', 'desc']`
    :   Teams view id

    `templates_view_id: Literal['asc', 'desc']`
    :   Templates view id

    `tertiary_timezone: Literal['asc', 'desc']`
    :   Tertiary timezone

    `texting_email_notifications: Literal['asc', 'desc']`
    :   Texting email notifications

    `title: Literal['asc', 'desc']`
    :   Title

    `unknown_reply_email_enabled: Literal['asc', 'desc']`
    :   Unknown reply email enabled

    `updated_at: Literal['asc', 'desc']`
    :   Updated at

    `updater: Literal['asc', 'desc']`
    :   Updater

    `use_sales_navigator_for_linked_in_tasks: Literal['asc', 'desc']`
    :   Use sales navigator for linked in tasks

    `user_guid: Literal['asc', 'desc']`
    :   User guid

    `username: Literal['asc', 'desc']`
    :   Username

    `users_view_id: Literal['asc', 'desc']`
    :   Users view id

    `voicemail_notification_enabled: Literal['asc', 'desc']`
    :   Voicemail notification enabled

    `voicemail_prompts: Literal['asc', 'desc']`
    :   Voicemail prompts

    `weekly_digest_email_enabled: Literal['asc', 'desc']`
    :   Weekly digest email enabled

<a id="UsersStartswithCondition"></a>

`UsersStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.outreach.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accounts_view_id: str`
    :   Accounts view id

    `active_prospects_count: str`
    :   Active prospects count

    `activity_notifications_disabled: str`
    :   Activity notifications disabled

    `batches: str`
    :   Batches

    `batches_view_id: str`
    :   Batches view id

    `bounce_warning_email_enabled: str`
    :   Bounce warning email enabled

    `bridge_phone: str`
    :   Bridge phone

    `bridge_phone_extension: str`
    :   Bridge phone extension

    `buyer_language_preference: str`
    :   Buyer language preference

    `calendar: str`
    :   Calendar

    `calendar_events_view_id: str`
    :   Calendar events view id

    `calls_view_id: str`
    :   Calls view id

    `content_categories: str`
    :   Content categories

    `content_category_ownerships: str`
    :   Content category ownerships

    `controlled_tab_default: str`
    :   Controlled tab default

    `created_at: str`
    :   Created at

    `creator: str`
    :   Creator

    `current_sign_in_at: str`
    :   Current sign in at

    `custom1: str`
    :   Custom field 1

    `custom2: str`
    :   Custom field 2

    `custom3: str`
    :   Custom field 3

    `custom4: str`
    :   Custom field 4

    `custom5: str`
    :   Custom field 5

    `daily_digest_email_enabled: str`
    :   Daily digest email enabled

    `default_ruleset_id: str`
    :   Default ruleset id

    `default_schedule_id: str`
    :   Default schedule id

    `duties: str`
    :   Duties

    `duties_set_at: str`
    :   Duties set at

    `email: str`
    :   Email

    `enable_voice_recordings: str`
    :   Enable voice recordings

    `engagement_emails_enabled: str`
    :   Engagement emails enabled

    `favorites: str`
    :   Favorites

    `first_name: str`
    :   First name

    `global_id: str`
    :   Global id

    `id: str`
    :   Unique user identifier

    `imports_view_id: str`
    :   Imports view id

    `inbound_bridge_phone: str`
    :   Inbound bridge phone

    `inbound_bridge_phone_extension: str`
    :   Inbound bridge phone extension

    `inbound_call_behavior: str`
    :   Inbound call behavior

    `inbound_phone_type: str`
    :   Inbound phone type

    `inbound_voicemail_custom_message_text: str`
    :   Inbound voicemail custom message text

    `inbound_voicemail_message_text_voice: str`
    :   Inbound voicemail message text voice

    `inbound_voicemail_prompt_type: str`
    :   Inbound voicemail prompt type

    `job_role: str`
    :   Job role

    `kaia_recordings_view_id: str`
    :   Kaia recordings view id

    `keep_bridge_phone_connected: str`
    :   Keep bridge phone connected

    `language_preference: str`
    :   Language preference

    `last_name: str`
    :   Last name

    `last_sign_in_at: str`
    :   Last sign in at

    `link_to_sequence_state_in_task_flow: str`
    :   Link to sequence state in task flow

    `live_listen_view_id: str`
    :   Live listen view id

    `locked: str`
    :   Locked

    `mailbox: str`
    :   Mailbox

    `mailbox_error_email_enabled: str`
    :   Mailbox error email enabled

    `mailboxes: str`
    :   Mailboxes

    `mailings_delivered_count: str`
    :   Mailings delivered count

    `mailings_replied_count: str`
    :   Mailings replied count

    `mailings_view_id: str`
    :   Mailings view id

    `meeting_engagement_notification_enabled: str`
    :   Meeting engagement notification enabled

    `meeting_types_view_id: str`
    :   Meeting types view id

    `name: str`
    :   Name

    `notifications_enabled: str`
    :   Notifications enabled

    `oce_click_to_dial_everywhere: str`
    :   Oce click to dial everywhere

    `oce_gmail_toolbar: str`
    :   Oce gmail toolbar

    `oce_gmail_tracking_state: str`
    :   Oce gmail tracking state

    `oce_salesforce_email_decorating: str`
    :   Oce salesforce email decorating

    `oce_salesforce_phone_decorating: str`
    :   Oce salesforce phone decorating

    `oce_universal_task_flow: str`
    :   Oce universal task flow

    `oce_window_mode: str`
    :   Oce window mode

    `onboarded_at: str`
    :   Onboarded at

    `opportunities_view_id: str`
    :   Opportunities view id

    `orca_standalone_enabled: str`
    :   Orca standalone enabled

    `outbound_voicemails: str`
    :   Outbound voicemails

    `password_expires_at: str`
    :   Password expires at

    `phone: str`
    :   Phone

    `phone_country_code: str`
    :   Phone country code

    `phone_number: str`
    :   Phone number

    `phone_type: str`
    :   Phone type

    `phones: str`
    :   Phones

    `phones_view_id: str`
    :   Phones view id

    `plugin_alert_notification_enabled: str`
    :   Plugin alert notification enabled

    `preferred_voice_region: str`
    :   Preferred voice region

    `prefers_local_presence: str`
    :   Prefers local presence

    `primary_timezone: str`
    :   Primary timezone

    `profile: str`
    :   Profile

    `prospect_detail_default: str`
    :   Prospect detail default

    `prospects_view_id: str`
    :   Prospects view id

    `recipients: str`
    :   Recipients

    `reports_sequence_performance_view_id: str`
    :   Reports sequence performance view id

    `reports_team_perf_view_id: str`
    :   Reports team perf view id

    `reports_team_performance_intraday_view_id: str`
    :   Reports team performance intraday view id

    `reports_team_performance_view_id: str`
    :   Reports team performance view id

    `reports_view_id: str`
    :   Reports view id

    `role: str`
    :   Role

    `scim_external_id: str`
    :   Scim external id

    `scim_source: str`
    :   Scim source

    `secondary_timezone: str`
    :   Secondary timezone

    `send_invite_fallback: str`
    :   Send invite fallback

    `sender_notifications_excluded: str`
    :   Sender notifications excluded

    `sequence_states_view_id: str`
    :   Sequence states view id

    `sequences_view_id: str`
    :   Sequences view id

    `sms_phone: str`
    :   Sms phone

    `snippets_view_id: str`
    :   Snippets view id

    `tasks_due_count: str`
    :   Tasks due count

    `tasks_view_id: str`
    :   Tasks view id

    `teams: str`
    :   Teams

    `teams_view_id: str`
    :   Teams view id

    `templates_view_id: str`
    :   Templates view id

    `tertiary_timezone: str`
    :   Tertiary timezone

    `texting_email_notifications: str`
    :   Texting email notifications

    `title: str`
    :   Title

    `unknown_reply_email_enabled: str`
    :   Unknown reply email enabled

    `updated_at: str`
    :   Updated at

    `updater: str`
    :   Updater

    `use_sales_navigator_for_linked_in_tasks: str`
    :   Use sales navigator for linked in tasks

    `user_guid: str`
    :   User guid

    `username: str`
    :   Username

    `users_view_id: str`
    :   Users view id

    `voicemail_notification_enabled: str`
    :   Voicemail notification enabled

    `voicemail_prompts: str`
    :   Voicemail prompts

    `weekly_digest_email_enabled: str`
    :   Weekly digest email enabled