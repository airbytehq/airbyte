#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.utils.airbyte_secrets_utils import AirbyteSecretHelper

SECRET_VALUE = "i am a very sensitive secret"
ANOTHER_SECRET_VALUE = "also super secret"
NOT_SECRET_VALUE = "unimportant value"


def test_airbyte_secret_helper():
    sensitive_str = f"{SECRET_VALUE} {NOT_SECRET_VALUE} {SECRET_VALUE} {ANOTHER_SECRET_VALUE}"

    AirbyteSecretHelper.update_secrets([])
    filtered = AirbyteSecretHelper.filter_secrets(sensitive_str)
    assert filtered == sensitive_str

    AirbyteSecretHelper.update_secrets([SECRET_VALUE, ANOTHER_SECRET_VALUE])
    filtered = AirbyteSecretHelper.filter_secrets(sensitive_str)
    assert filtered == f"**** {NOT_SECRET_VALUE} **** ****"
