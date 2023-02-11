#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re


class GAQL:
    """
    Simple regex parser of Google Ads Query Language
    https://developers.google.com/google-ads/api/docs/query/grammar
    """

    REGEX = re.compile(
        r"""\s*
            SELECT\s+(?P<FieldNames>\S.*)
            \s+
            FROM\s+(?P<ResourceName>[a-z]([a-zA-Z_])*)
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

    def __init__(self, query):
        m = self.REGEX.match(query)
        if not m:
            raise Exception(f"incorrect GAQL query statement: {repr(query)}")

        self.FieldNames = [f.strip() for f in m.group("FieldNames").split(",")]
        for field in self.FieldNames:
            if not self.REGEX_FIELD_NAME.match(field):
                raise Exception(f"incorrect GAQL query statement: {repr(query)}")

        self.ResourceName = m.group("ResourceName")
        self.WhereClause = m.group("WhereClause")
        if self.WhereClause:
            self.WhereClause = self._normalize(self.WhereClause)
        self.OrderByClause = m.group("OrderByClause")
        if self.OrderByClause:
            self.OrderByClause = self._normalize(self.OrderByClause)
        self.LimitClause = m.group("LimitClause")
        if self.LimitClause:
            self.LimitClause = int(self.LimitClause)
        self.ParametersClause = m.group("ParametersClause")
        if self.ParametersClause:
            self.ParametersClause = self._normalize(self.ParametersClause)

    def __str__(self):
        FieldNames = ", ".join(self.FieldNames)
        query = f"SELECT {FieldNames} FROM {self.ResourceName}"
        if self.WhereClause:
            query += " WHERE " + self.WhereClause
        if self.OrderByClause:
            query += " ORDER BY " + self.OrderByClause
        if self.LimitClause:
            query += " LIMIT " + str(self.LimitClause)
        if self.ParametersClause:
            query += " PARAMETERS " + self.ParametersClause
        return query

    @staticmethod
    def _normalize(s):
        s = s.strip()
        return re.sub(r"\s+", " ", s)
