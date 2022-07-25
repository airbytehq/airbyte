from collections.abc import MutableMapping


class Level:
    def __init__(self, version: str):
        self.id = None
        self.name = None
        self.currency = None
        self.shortName = None
        self.isElimination = None
        self.isLinked = None
        self.workflowStatus = None
        self.isImportable = None
        self.attributes = None
        self.version = version
        # self.parent_level = None

    def parse_dict(self, d: dict) -> None:
        
        self.id = int(d.get("@id"))
        self.name = d.get("@name")
        self.currency = d.get("@currency")
        self.shortName = d.get("@shortName")
        self.isElimination = d.get("@isElimination")
        self.isLinked = d.get("@isLinked")
        self.workflowStatus = d.get("@workflowStatus")
        self.isImportable = d.get("@isImportable")
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
            "id": self.id,
            "name": self.name,
            "currency": self.currency,
            "short_name": self.shortName,
            "is_elimination": self.isElimination,
            "is_linked": self.isLinked,
            "workflow_status": self.workflowStatus,
            "is_important": self.isImportable,
            "attributes": str(self.parse_attributes(self.attributes)),
            "version": self.version
        }


def flatten_dict(d: MutableMapping, items: list, version:str) -> MutableMapping:

    if isinstance(d, list):
        for i in d:
            flatten_dict(i, items, version)
    else:
        dict_keys = list(d.keys())
        if "level" in dict_keys:
            flatten_dict(d["level"], items, version)
            lvl = Level(version=version)
            lvl.parse_dict(d)
            items.append(lvl.to_record())
        else:
            lvl = Level(version=version)
            lvl.parse_dict(d)
            items.append(lvl.to_record())
    
    return items


def handle_export_levels(d: MutableMapping, version: str) -> MutableMapping:
    data = d.get("response").get("output").get("levels").get("level")
    items = []

    return flatten_dict(d=data, items=items, version=version)
