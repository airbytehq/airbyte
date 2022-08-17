#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from enum import Enum


class YMSource:
    VIEWS = "hits"
    SESSIONS = "visits"

    def __str__(self):
        return self.value


class YMPrimaryKey:
    VIEWS = "ym:pv:watchID"
    SESSIONS = "ym:s:visitID"

    def __str__(self):
        return self.value


class YMCursor:
    VIEWS = "ym:pv:dateTime"
    SESSIONS = "ym:s:dateTime"

    def __str__(self):
        return self.value


class YMStatus:
    PROCESSED = "processed"

    def __str__(self):
        return self.value
