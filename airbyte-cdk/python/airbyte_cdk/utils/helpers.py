#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import weakref

CLASS_TO_INSTANCES = {}


def get_instance_number(instance):
    ":return: sequential number of instance of the same class"
    instances = CLASS_TO_INSTANCES.setdefault(instance.__class__, [])
    n = 0
    for n, ref in enumerate(instances, start=1):
        if ref() is instance:
            return n
    instances.append(weakref.ref(instance))
    n += 1
    return n
