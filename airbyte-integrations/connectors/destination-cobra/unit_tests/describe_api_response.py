# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict

from airbyte_cdk.test.mock_http import HttpResponse


class SalesforceFieldBuilder:
    def __init__(self):
        self._name = "sf_object_name"
        self._type = "string"
        self._template = {
            "aggregatable": True,
            "aiPredictionField": False,
            "autoNumber": False,
            "byteLength": 18,
            "calculated": False,
            "calculatedFormula": None,
            "cascadeDelete": False,
            "caseSensitive": False,
            "compoundFieldName": None,
            "controllerName": None,
            "createable": False,
            "custom": False,
            "defaultValue": None,
            "defaultValueFormula": None,
            "defaultedOnCreate": True,
            "dependentPicklist": False,
            "deprecatedAndHidden": False,
            "digits": 0,
            "displayLocationInDecimal": False,
            "encrypted": False,
            "externalId": False,
            "extraTypeInfo": None,
            "filterable": True,
            "filteredLookupInfo": None,
            "formulaTreatNullNumberAsZero": False,
            "groupable": True,
            "highScaleNumber": False,
            "htmlFormatted": False,
            "idLookup": True,
            "inlineHelpText": None,
            "label": "Contact ID",
            "length": 18,
            "mask": None,
            "maskType": None,
            "name": "Id",
            "nameField": False,
            "namePointing": False,
            "nillable": False,
            "permissionable": False,
            "picklistValues": [],
            "polymorphicForeignKey": False,
            "precision": 0,
            "queryByDistance": False,
            "referenceTargetField": None,
            "referenceTo": [],
            "relationshipName": None,
            "relationshipOrder": None,
            "restrictedDelete": False,
            "restrictedPicklist": False,
            "scale": 0,
            "searchPrefilterable": False,
            "soapType": "tns:ID",
            "sortable": True,
            "type": "id",
            "unique": False,
            "updateable": False,
            "writeRequiresMasterRead": False,
        }

    def with_name(self, name: str) -> "SalesforceFieldBuilder":
        self._template["name"] = name
        return self

    def with_type(self, _type: str) -> "SalesforceFieldBuilder":
        self._template["type"] = _type
        return self

    def build(self) -> Dict[str, Any]:
        return self._template


class SalesforceDescribeResponseBuilder:
    def __init__(self, sf_object: str) -> None:
        self._template = {
            "actionOverrides": [],
            "activateable": False,
            "associateEntityType": None,
            "associateParentEntity": None,
            "childRelationships": [],
            "compactLayoutable": True,
            "createable": True,
            "custom": False,
            "customSetting": False,
            "deepCloneable": False,
            "defaultImplementation": None,
            "deletable": True,
            "deprecatedAndHidden": False,
            "extendedBy": None,
            "extendsInterfaces": None,
            "feedEnabled": True,
            "fields": [],
            "hasSubtypes": False,
            "implementedBy": None,
            "implementsInterfaces": None,
            "isInterface": False,
            "isSubtype": False,
            "keyPrefix": "003",
            "label": sf_object,
            "labelPlural": f"{sf_object}s",
            "layoutable": True,
            "listviewable": None,
            "lookupLayoutable": None,
            "mergeable": True,
            "mruEnabled": True,
            "name": "Contact",
            "namedLayoutInfos": [],
            "networkScopeFieldName": None,
            "queryable": True,
            "recordTypeInfos": [],
            "replicateable": True,
            "retrieveable": True,
            "searchLayoutable": True,
            "searchable": True,
            "sobjectDescribeOption": "FULL",
            "supportedScopes": [],
            "triggerable": True,
            "undeletable": True,
            "updateable": True,
            "urls": {
                "compactLayouts": "/services/data/v61.0/sobjects/Contact/describe/compactLayouts",
                "rowTemplate": "/services/data/v61.0/sobjects/Contact/{ID}",
                "approvalLayouts": "/services/data/v61.0/sobjects/Contact/describe/approvalLayouts",
                "uiDetailTemplate": "https://airbyte--retl2.sandbox.my.salesforce.com/{ID}",
                "uiEditTemplate": "https://airbyte--retl2.sandbox.my.salesforce.com/{ID}/e",
                "listviews": "/services/data/v61.0/sobjects/Contact/listviews",
                "describe": "/services/data/v61.0/sobjects/Contact/describe",
                "uiNewRecord": "https://airbyte--retl2.sandbox.my.salesforce.com/003/e",
                "quickActions": "/services/data/v61.0/sobjects/Contact/quickActions",
                "layouts": "/services/data/v61.0/sobjects/Contact/describe/layouts",
                "sobject": "/services/data/v61.0/sobjects/Contact",
            },
        }

    def with_field(self, field: SalesforceFieldBuilder) -> "SalesforceDescribeResponseBuilder":
        self._template["fields"].append(field.build())
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps(self._template), 200)
