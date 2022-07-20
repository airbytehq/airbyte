from collections.abc import MutableMapping
from datetime import datetime


class Version:
    def __init__(self):
        self.id = None
        self.name = None
        self.type = None
        self.is_locked = None
        self.date = None

    def parse_dict(self, d: dict) -> None:
        self.id = d.get("@id")
        self.name = d.get("@name")
        self.type = d.get("@type")
        self.is_locked = d.get("@isLocked")

        date = self.name[3:]
        if self.is_valid_version and self.is_lbe:
            self.date = datetime.strptime(date, "%m%y").strftime("%Y-%m-%d")
        elif self.is_valid_version and self.is_predictive:
            self.date = f"{date}-01-01"
    
    def to_record(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "is_locked": self.is_locked,
            "date": self.date
        }

    @property
    def is_lbe(self) -> bool:
        return self.name.startswith("LBE") and len(self.name) == 7 and self.type == "PLANNING" and self.is_locked == "true"

    @property
    def is_predictive(self) -> bool:
        return self.name.startswith("AOP") and len(self.name) == 7 and self.type == "PLANNING" and self.is_locked == "true"

    @property
    def is_valid_version(self) -> bool:
        return len(self.name) == 7 and (self.is_lbe or self.is_predictive)

    @staticmethod
    def find_versions(versions: list) -> dict:
        latest_date = "1900-01-01"
        second_to_latest_date = "1900-01-01"
        predictive_year = "1900-01-01"

        for version in versions:
            if not version.is_valid_version:
                continue
            version_date = version.date
            if version.is_predictive:
                if predictive_year < version_date:
                    predictive_year = version_date
            elif version.is_lbe:
                if latest_date < version_date:
                    latest_date = version_date
                if second_to_latest_date < version_date and latest_date > version_date:
                    second_to_latest_date = version_date
        
        return {
            "latest": f"LBE{datetime.strptime(latest_date, '%Y-%m-%d').strftime('%m%y')}",
            "second_to_latest": f"LBE{datetime.strptime(second_to_latest_date, '%Y-%m-%d').strftime('%m%y')}",
            "predictive": f"AOP{datetime.strptime(predictive_year, '%Y-%m-%d').strftime('%Y')}",
        }


def parse_export_versions(d: MutableMapping) -> dict:

    versions = []
    for i in d:
        v = Version()
        v.parse_dict(i)
        versions.append(v)
    
    return Version().find_versions(versions)
