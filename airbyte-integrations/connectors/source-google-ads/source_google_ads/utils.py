#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from dataclasses import dataclass
from typing import Optional, Tuple

# maps stream name to name of resource in Google Ads
REPORT_MAPPING = {
    "accounts": "customer",
    "account_labels": "customer_label",
    "account_performance_report": "customer",
    "ad_group_ads": "ad_group_ad",
    "ad_group_ad_labels": "ad_group_ad_label",
    "ad_group_ad_report": "ad_group_ad",
    "ad_groups": "ad_group",
    "ad_group_bidding_strategies": "ad_group",
    "ad_group_criterions": "ad_group_criterion",
    "ad_group_criterion_labels": "ad_group_criterion_label",
    "ad_group_labels": "ad_group_label",
    "ad_listing_group_criterions": "ad_group_criterion",
    "audience": "audience",
    "campaigns": "campaign",
    "campaign_real_time_bidding_settings": "campaign",
    "campaign_criterion": "campaign_criterion",
    "campaign_bidding_strategies": "campaign",
    "campaign_budget": "campaign_budget",
    "campaign_labels": "campaign_label",
    "change_status": "change_status",
    "click_view": "click_view",
    "display_keyword_performance_report": "display_keyword_view",
    "display_topics_performance_report": "topic_view",
    "geographic_report": "geographic_view",
    "keyword_report": "keyword_view",
    "labels": "label",
    "service_accounts": "customer",
    "shopping_performance_report": "shopping_performance_view",
    "user_interest": "user_interest",
    "user_location_report": "user_location_view",
}


@dataclass(repr=False, eq=False, frozen=True)
class GAQL:
    """
    Simple regex parser of Google Ads Query Language
    https://developers.google.com/google-ads/api/docs/query/grammar
    """

    fields: Tuple[str]
    resource_name: str
    where: str
    order_by: str
    limit: Optional[int]
    parameters: str

    REGEX = re.compile(
        r"""\s*
            SELECT\s+(?P<FieldNames>\S.*)
            \s+
            FROM\s+(?P<ResourceNames>[a-z][a-zA-Z_]*(\s*,\s*[a-z][a-zA-Z_]*)*)
            \s*
            (\s+WHERE\s+(?P<WhereClause>\S.*?))?
            (\s+ORDER\s+BY\s+(?P<OrderByClause>\S.*?))?
            (\s+LIMIT\s+(?P<LimitClause>[1-9]([0-9])*))?
            \s*
            (\s+PARAMETERS\s+(?P<ParametersClause>\S.*?))?
            $""",
        flags=re.I | re.DOTALL | re.VERBOSE,
    )

    REGEX_FIELD_NAME = re.compile(r"^[a-z][a-z0-9._]*$", re.I)

    @classmethod
    def parse(cls, query):
        m = cls.REGEX.match(query)
        if not m:
            raise ValueError

        fields = [f.strip() for f in m.group("FieldNames").split(",")]
        for field in fields:
            if not cls.REGEX_FIELD_NAME.match(field):
                raise ValueError

        resource_names = re.split(r"\s*,\s*", m.group("ResourceNames"))
        if len(resource_names) > 1:
            raise ValueError
        resource_name = resource_names[0]

        where = cls._normalize(m.group("WhereClause") or "")
        order_by = cls._normalize(m.group("OrderByClause") or "")
        limit = m.group("LimitClause")
        if limit:
            limit = int(limit)
        parameters = cls._normalize(m.group("ParametersClause") or "")
        return cls(tuple(fields), resource_name, where, order_by, limit, parameters)

    def __str__(self):
        fields = ", ".join(self.fields)
        query = f"SELECT {fields} FROM {self.resource_name}"
        if self.where:
            query += " WHERE " + self.where
        if self.order_by:
            query += " ORDER BY " + self.order_by
        if self.limit is not None:
            query += " LIMIT " + str(self.limit)
        if self.parameters:
            query += " PARAMETERS " + self.parameters
        return query

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _normalize(s):
        s = s.strip()
        return re.sub(r"\s+", " ", s)

    def set_where(self, value: str):
        return self.__class__(self.fields, self.resource_name, value, self.order_by, self.limit, self.parameters)

    def set_limit(self, value: int):
        return self.__class__(self.fields, self.resource_name, self.where, self.order_by, value, self.parameters)

    def append_field(self, value):
        fields = list(self.fields)
        fields.append(value)
        return self.__class__(tuple(fields), self.resource_name, self.where, self.order_by, self.limit, self.parameters)
