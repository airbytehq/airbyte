#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


class YMSource:
    VIEWS = "hits"
    SESSIONS = "visits"

    def __str__(self):
        return self.value


class YMPrimaryKey:
    VIEWS = "watchID"
    SESSIONS = "visitID"

    def __str__(self):
        return self.value


class YMCursor:
    VIEWS = "dateTime"
    SESSIONS = "dateTime"

    def __str__(self):
        return self.value


class YMStatus:
    PROCESSED = "processed"

    def __str__(self):
        return self.value
