#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import hashlib

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation

interpolation = JinjaInterpolation()


def test_hash_md5_no_salt():
    input_string = "abcd"
    s = "{{ '%s' | hash('md5') }}" % input_string
    filter_hash = interpolation.eval(s, config={})

    # compute expected hash calling hashlib directly
    hash_obj = hashlib.md5()
    hash_obj.update(str(input_string).encode("utf-8"))
    hashlib_computed_hash = hash_obj.hexdigest()

    assert filter_hash == hashlib_computed_hash


def test_hash_md5_on_numeric_value():
    input_value = 123.456
    s = "{{ %f | hash('md5') }}" % input_value
    filter_hash = interpolation.eval(s, config={})

    # compute expected hash calling hashlib directly
    hash_obj = hashlib.md5()
    hash_obj.update(str(input_value).encode("utf-8"))
    hashlib_computed_hash = hash_obj.hexdigest()

    assert filter_hash == hashlib_computed_hash


def test_hash_md5_with_salt():
    input_string = "test_input_string"
    input_salt = "test_input_salt"

    s = "{{ '%s' | hash('md5', '%s' ) }}" % (input_string, input_salt)
    filter_hash = interpolation.eval(s, config={})

    # compute expected value calling hashlib directly
    hash_obj = hashlib.md5()
    hash_obj.update(str(input_string + input_salt).encode("utf-8"))
    hashlib_computed_hash = hash_obj.hexdigest()

    assert filter_hash == hashlib_computed_hash
