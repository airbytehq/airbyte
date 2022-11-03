#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


# RecordTransformation is depended upon by every class in this module (since it's the abc everything implements). For this reason,
# the order of imports matters i.e: this file must fully import RecordTransformation before importing anything which depends on RecordTransformation
# Otherwise there will be a circular dependency (load order will be init.py --> RemoveFields (which tries to import RecordTransformation) -->
# init.py --> circular dep error, since loading this file causes it to try to import itself down the line.
# so we add the split directive below to tell isort to sort imports while keeping RecordTransformation as the first import
from .transformation import RecordTransformation

# isort: split
from .add_fields import AddFields
from .remove_fields import RemoveFields

__all__ = ["AddFields", "RecordTransformation", "RemoveFields"]
