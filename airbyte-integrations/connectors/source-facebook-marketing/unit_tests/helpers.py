#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from datetime import datetime
from source_facebook_marketing.utils import ValidationDateException, validate_date_field


def test_validate_date_field():
    field_name = "test_field_name"
    date = datetime(2008, 1, 1)
    with pytest.raises(ValidationDateException):
        assert validate_date_field(field_name, date)

