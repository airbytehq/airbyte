#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from base64 import b64encode

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


def test_get_value_from_config():
    interpolation = JinjaInterpolation()
    s = "{{ config['date'] }}"
    config = {"date": "2022-01-01"}
    val = interpolation.eval(s, config)
    assert val == "2022-01-01"


def test_get_value_from_stream_slice():
    interpolation = JinjaInterpolation()
    s = "{{ stream_slice['date'] }}"
    config = {"date": "2022-01-01"}
    stream_slice = {"date": "2020-09-09"}
    val = interpolation.eval(s, config, **{"stream_slice": stream_slice})
    assert val == "2020-09-09"


def test_get_value_from_a_list_of_mappings():
    interpolation = JinjaInterpolation()
    s = "{{ records[0]['date'] }}"
    config = {"date": "2022-01-01"}
    records = [{"date": "2020-09-09"}]
    val = interpolation.eval(s, config, **{"records": records})
    assert val == "2020-09-09"


def test_encode_latin1():
    interpolation = JinjaInterpolation()
    s = "{{ encode('hello', 'latin1') ~ ':' ~ encode('world', 'latin1') }}"
    config = {"username": "airbyte", "password": "s0Secure"}
    val = interpolation.eval(s, config)
    assert val == "b'hello':b'world'"


def test_encode_base64():
    interpolation = JinjaInterpolation()
    s = "{{ base64(encode('hello', 'latin1')) }}"
    config = {"username": "airbyte", "password": "s0Secure"}
    val = interpolation.eval(s, config)
    assert val == "aGVsbG8="


def test_encode_base64_custom_string():
    interpolation = JinjaInterpolation()
    s = "{{ base64(encode(config['username'] + ':' + config['password'], 'latin1'), 'ascii') }}"
    config = {"username": "airbyte", "password": "s0Secure"}
    val = interpolation.eval(s, config)
    encoded_hello = "airbyte:s0Secure".encode("latin1")
    expected_string = b64encode(encoded_hello).decode("ascii")
    assert val == expected_string


def test_encode_base64_custom_string_different_encoding():
    interpolation = JinjaInterpolation()
    s = "{{ base64(encode(config['username'] + ':' + config['password'], 'utf8'), 'utf8') }}"
    config = {"username": "airbyte", "password": "s0Secure"}
    val = interpolation.eval(s, config)
    encoded_hello = "airbyte:s0Secure".encode("latin1")
    expected_string = b64encode(encoded_hello).decode("ascii")
    assert val == expected_string


def test_encode_base64_custom_string_different_encoding_again():
    interpolation = JinjaInterpolation()
    s = "{{ base64(encode(config['username'] + ':' + config['password'], 'ascii'), 'ascii') }}"
    config = {"username": "airbyte", "password": "s0Secure"}
    val = interpolation.eval(s, config)
    encoded_hello = "airbyte:s0Secure".encode("latin1")
    expected_string = b64encode(encoded_hello).decode("ascii")
    assert val == expected_string
