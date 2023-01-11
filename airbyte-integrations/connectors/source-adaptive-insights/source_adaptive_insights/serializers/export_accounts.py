from collections.abc import MutableMapping
from typing import Union


class Account:
    def __init__(self, version: str, parent_code: str = None, parent_name: str = None):
        self.id = None
        self.code = None
        self.name = None
        self.description = None
        self.timeStratum = None
        self.displayAs = None
        self.accountTypeCode = None
        self.decimalPrecision = None
        self.isAssumption = None
        self.suppressZeroes = None
        self.isDefaultRoot = None
        self.shortName = None
        self.isIntercompany = None
        self.balanceType = None
        self.isLinked = None
        self.owningSheetId = None
        self.isSystem = None
        self.isImportable = None
        self.dataEntryType = None
        self.planBy = None
        self.actualsBy = None
        self.timeRollup = None
        self.timeWeightAcctId = None
        self.levelDimRollup = None
        self.levelDimWeightAcctId = None
        self.rollupText = None
        self.startExpanded = None
        self.hasSalaryDetail = None
        self.dataPrivacy = None
        self.isBreakbackEligible = None
        self.subType = None
        self.enableActuals = None
        self.isGroup = None
        self.hasFormula = None
        self.attributes = None
        self.version = version
        self.parent_code = parent_code
        self.parent_name = parent_name

    def parse_dict(self, d: Union[dict, MutableMapping]) -> None:

        self.id = d.get("@id")
        self.code = d.get("@code")
        self.name = d.get("@name")
        self.description = d.get("@description")
        self.timeStratum = d.get("@timeStratum")
        self.displayAs = d.get("@displayAs")
        self.accountTypeCode = d.get("@accountTypeCode")
        self.decimalPrecision = d.get("@decimalPrecision")
        self.isAssumption = d.get("isAssumption")
        self.suppressZeroes = d.get("@suppressZeroes")
        self.isDefaultRoot = d.get("@isDefaultRoot")
        self.shortName = d.get("@shortName")
        self.isIntercompany = d.get("@isIntercompany")
        self.balanceType = d.get("@balanceType")
        self.isLinked = d.get("@isLinked")
        self.owningSheetId = d.get("@owningSheetId")
        self.isSystem = d.get("@isSystem")
        self.isImportable = d.get("isImportable")
        self.dataEntryType = d.get("@dataEntryType")
        self.planBy = d.get("@planBy")
        self.actualsBy = d.get("@actualsBy")
        self.timeRollup = d.get("@timeRollup")
        self.timeWeightAcctId = d.get("@timeWeightAcctId")
        self.levelDimRollup = d.get("@levelDimRollup")
        self.levelDimWeightAcctId = d.get("@levelDimWeightAcctId")
        self.rollupText = d.get("@rollupText")
        self.startExpanded = d.get("startExpanded")
        self.hasSalaryDetail = d.get("@hasSalaryDetail")
        self.dataPrivacy = d.get("@dataPrivacy")
        self.isBreakbackEligible = d.get("@isBreakbackEligible")
        self.subType = d.get("@subType")
        self.enableActuals = d.get("@enableActuals")
        self.isGroup = d.get("@isGroup")
        self.hasFormula = d.get("@hasFormula")
        self.attributes = d.get("attributes", None)

    @staticmethod
    def parse_attributes(d: dict) -> dict:
        if not d:
            return None

        attribute_records = []

        attributes = d.get("attribute")
        if isinstance(attributes, list):
            for attribute in attributes:
                record = {}
                for k, v in attribute.items():
                    record[k.replace("@", "")] = v

                attribute_records.append(record)
        elif isinstance(attributes, dict):
            record = {}
            for k, v in attributes.items():
                record[k.replace("@", "")] = v
            attribute_records.append(record)
        else:
            raise NotImplementedError()

        return attribute_records

    def to_record(self) -> dict:
        return {
            "id": int(self.id),
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "time_stratum": self.timeStratum,
            "display_as": self.displayAs,
            "account_type_code": self.accountTypeCode,
            "decimal_precision": self.decimalPrecision,
            "is_assumption": self.isAssumption,
            "suppress_zeroes": self.suppressZeroes,
            "is_default_root": self.isDefaultRoot,
            "short_name": self.shortName,
            "is_intercompany": self.isIntercompany,
            "balance_type": self.balanceType,
            "is_linked": self.isLinked,
            "owning_sheet_id": self.owningSheetId,
            "is_system": self.isSystem,
            "is_importable": self.isImportable,
            "data_entry_type": self.dataEntryType,
            "plan_by": self.planBy,
            "actuals_by": self.actualsBy,
            "time_rollup": self.timeRollup,
            "time_weight_acct_id": self.timeWeightAcctId,
            "level_dim_rollup": self.levelDimRollup,
            "level_dim_weight_acct_id": self.levelDimWeightAcctId,
            "rollup_text": self.rollupText,
            "start_expanded": self.startExpanded,
            "has_salary_detail": self.hasSalaryDetail,
            "data_privacy": self.dataPrivacy,
            "is_breakback_eligible": self.isBreakbackEligible,
            "sub_type": self.subType,
            "enable_actuals": self.enableActuals,
            "is_group": self.isGroup,
            "has_formula": self.hasFormula,
            "attributes": str(self.parse_attributes(self.attributes)),
            "version": self.version,
            "rollup_to_code": self.parent_code,
            "rollup_to_text": self.parent_name
        }


def flatten_dict(d: MutableMapping,
                 items: Union[list, MutableMapping],
                 version: str,
                 parent_code=None,
                 parent_name=None) -> MutableMapping:
    if isinstance(d, list):
        for i in d:
            flatten_dict(i, items, version, parent_code, parent_name)
    else:
        dict_keys = list(d.keys())
        if "account" in dict_keys:
            lvl = Account(version=version, parent_code=parent_code, parent_name=parent_name)
            lvl.parse_dict(d)
            flatten_dict(d["account"], items, version, lvl.code, lvl.name)

            items.append(lvl.to_record())
        else:
            lvl = Account(version=version, parent_code=parent_code, parent_name=parent_name)
            lvl.parse_dict(d)
            items.append(lvl.to_record())

    return items


def handle_export_accounts(d: dict, version: str) -> list:
    data = d.get("response").get("output").get("accounts").get("account")
    items = []

    return flatten_dict(d=data, items=items, version=version)
