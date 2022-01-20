#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


def create_test_task(a=12):
    if a == 12:
        return 13
    elif a == 22:
        return 23
    else:
        return 44
