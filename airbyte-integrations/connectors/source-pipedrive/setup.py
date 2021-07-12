#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "pendulum~=2.1",
    "requests~=2.25",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
]

setup(
    name="source_pipedrive",
    description="Source implementation for Pipedrive.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)


# {
#     "$schema": "http://json-schema.org/draft-07/schema",
#     "$id": "http://example.com/example.json",
#     "type": "object",
#     "title": "The root schema",
#     "description": "The root schema comprises the entire JSON document.",
#     "default": {},
#     "examples": [
#         {
#             "id": 1,
#             "name": "John Doe",
#             "default_currency": "EUR",
#             "locale": "et_EE",
#             "lang": 1,
#             "email": "john@pipedrive.com",
#             "phone": "0000-0001",
#             "activated": true,
#             "last_login": "2019-11-21 08:45:56",
#             "created": "2018-11-13 09:16:26",
#             "modified": "2019-11-21 08:45:56",
#             "signup_flow_variation": "google",
#             "has_created_company": true,
#             "is_admin": 1,
#             "active_flag": true,
#             "timezone_name": "Europe/Berlin",
#             "timezone_offset": "+03:00",
#             "role_id": 1,
#             "icon_url": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e0/WPVG_icon_2016.svg/1024px-WPVG_icon_2016.svg.png",
#             "is_you": true
#         }
#     ],
#     "required": [
#         "id",
#         "name",
#         "default_currency",
#         "locale",
#         "lang",
#         "email",
#         "phone",
#         "activated",
#         "last_login",
#         "created",
#         "modified",
#         "signup_flow_variation",
#         "has_created_company",
#         "is_admin",
#         "active_flag",
#         "timezone_name",
#         "timezone_offset",
#         "role_id",
#         "icon_url",
#         "is_you"
#     ],
#     "properties": {
#         "id": {
#             "$id": "#/properties/id",
#             "type": "integer",
#             "title": "The id schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": 0,
#             "examples": [
#                 1
#             ]
#         },
#         "name": {
#             "$id": "#/properties/name",
#             "type": "string",
#             "title": "The name schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "John Doe"
#             ]
#         },
#         "default_currency": {
#             "$id": "#/properties/default_currency",
#             "type": "string",
#             "title": "The default_currency schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "EUR"
#             ]
#         },
#         "locale": {
#             "$id": "#/properties/locale",
#             "type": "string",
#             "title": "The locale schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "et_EE"
#             ]
#         },
#         "lang": {
#             "$id": "#/properties/lang",
#             "type": "integer",
#             "title": "The lang schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": 0,
#             "examples": [
#                 1
#             ]
#         },
#         "email": {
#             "$id": "#/properties/email",
#             "type": "string",
#             "title": "The email schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "john@pipedrive.com"
#             ]
#         },
#         "phone": {
#             "$id": "#/properties/phone",
#             "type": "string",
#             "title": "The phone schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "0000-0001"
#             ]
#         },
#         "activated": {
#             "$id": "#/properties/activated",
#             "type": "boolean",
#             "title": "The activated schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": false,
#             "examples": [
#                 true
#             ]
#         },
#         "last_login": {
#             "$id": "#/properties/last_login",
#             "type": "string",
#             "title": "The last_login schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "2019-11-21 08:45:56"
#             ]
#         },
#         "created": {
#             "$id": "#/properties/created",
#             "type": "string",
#             "title": "The created schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "2018-11-13 09:16:26"
#             ]
#         },
#         "modified": {
#             "$id": "#/properties/modified",
#             "type": "string",
#             "title": "The modified schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "2019-11-21 08:45:56"
#             ]
#         },
#         "signup_flow_variation": {
#             "$id": "#/properties/signup_flow_variation",
#             "type": "string",
#             "title": "The signup_flow_variation schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "google"
#             ]
#         },
#         "has_created_company": {
#             "$id": "#/properties/has_created_company",
#             "type": "boolean",
#             "title": "The has_created_company schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": false,
#             "examples": [
#                 true
#             ]
#         },
#         "is_admin": {
#             "$id": "#/properties/is_admin",
#             "type": "integer",
#             "title": "The is_admin schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": 0,
#             "examples": [
#                 1
#             ]
#         },
#         "active_flag": {
#             "$id": "#/properties/active_flag",
#             "type": "boolean",
#             "title": "The active_flag schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": false,
#             "examples": [
#                 true
#             ]
#         },
#         "timezone_name": {
#             "$id": "#/properties/timezone_name",
#             "type": "string",
#             "title": "The timezone_name schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "Europe/Berlin"
#             ]
#         },
#         "timezone_offset": {
#             "$id": "#/properties/timezone_offset",
#             "type": "string",
#             "title": "The timezone_offset schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "+03:00"
#             ]
#         },
#         "role_id": {
#             "$id": "#/properties/role_id",
#             "type": "integer",
#             "title": "The role_id schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": 0,
#             "examples": [
#                 1
#             ]
#         },
#         "icon_url": {
#             "$id": "#/properties/icon_url",
#             "type": "string",
#             "title": "The icon_url schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": "",
#             "examples": [
#                 "https://upload.wikimedia.org/wikipedia/en/thumb/e/e0/WPVG_icon_2016.svg/1024px-WPVG_icon_2016.svg.png"
#             ]
#         },
#         "is_you": {
#             "$id": "#/properties/is_you",
#             "type": "boolean",
#             "title": "The is_you schema",
#             "description": "An explanation about the purpose of this instance.",
#             "default": false,
#             "examples": [
#                 true
#             ]
#         }
#     },
#     "additionalProperties": true
# }
