#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


def adaptTypeToEnum(type: int):
    if type == 1:
        return "HTTP"
    elif type == 2:
        return "Keyword"
    elif type == 3:
        return "Ping"
    elif type == 4:
        return "Port"
    elif type == 5:
        return "Heartbeat"


def adaptSubTypeToEnum(subtype: int):
    if subtype == 1:
        return "HTTP"
    elif subtype == 2:
        return "HTTPS"
    elif subtype == 3:
        return "FTP"
    elif subtype == 4:
        return "SMTP"
    elif subtype == 5:
        return "POP3"
    elif subtype == 6:
        return "IMAP"
    elif subtype == 99:
        return "Custom Port"


def adaptStatusToEnum(status: int):
    if status == 0:
        return "PAUSED"
    elif status == 1:
        return "PENDING"
    elif status == 2:
        return "UP"
    elif status == 8:
        return "MAYBE_DOWN"
    elif status == 9:
        return "DOWN"
