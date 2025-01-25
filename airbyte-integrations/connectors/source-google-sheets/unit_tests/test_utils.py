#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import pytest
from source_google_sheets.utils import exception_description_by_status_code, name_conversion, safe_name_conversion


def test_name_conversion():
    assert name_conversion("My_Name") == "my_name"
    assert name_conversion("My Name") == "my_name"
    assert name_conversion("MyName") == "my_name"
    assert name_conversion("mYName") == "m_yname"
    assert name_conversion("MyName123") == "my_name_123"
    assert name_conversion("My123name") == "my_123_name"
    assert name_conversion("My_Name!") == "my_name_"
    assert name_conversion("My_Name____c") == "my_name_c"
    assert name_conversion("1MyName") == "_1_my_name"
    assert name_conversion("!MyName") == "_my_name"
    assert name_conversion("прівит світ") == "privit_svit"


def test_safe_name_conversion():
    with pytest.raises(Exception) as exc_info:
        safe_name_conversion("*****")
    assert exc_info.value.args[0] == "initial string '*****' converted to empty"
