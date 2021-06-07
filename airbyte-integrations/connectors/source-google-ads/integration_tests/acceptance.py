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


import pytest

pytest_plugins = ("source_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """ This fixture is a placeholder for external resources that acceptance test might require."""
    # TODO: setup test dependencies if needed. otherwise remove the TODO comments
    yield
    # TODO: clean up test dependencies


"""
This won't work until we get sample credentials 
"""

# def test_incremental_sync():
#     google_ads_client = SourceGoogleAds()
#     state = "2021-05-24"
#     records = google_ads_client.read(AirbyteLogger(), SAMPLE_CONFIG, ConfiguredAirbyteCatalog.parse_obj(SAMPLE_CATALOG), {"ad_group_ad_report": {
#         "date": state
#     }})
#     current_state = (date.fromisoformat(state) -
#                      relativedelta(days=14)).isoformat()
#     for record in records:
#         if record and record.type == Type.STATE:
#             current_state = record.state.data["ad_group_ad_report"]["date"]
#         if record and record.type == Type.RECORD:
#             assert record.record.data["date"] >= current_state

#     # Next sync
#     state = "2021-06-04"
#     records = google_ads_client.read(AirbyteLogger(), SAMPLE_CONFIG, ConfiguredAirbyteCatalog.parse_obj(SAMPLE_CATALOG), {"ad_group_ad_report": {
#         "date": state
#     }})
#     current_state = (date.fromisoformat(state) -
#                      relativedelta(days=14)).isoformat()

#     for record in records:
#         if record and record.type == Type.STATE:
#             current_state = record.state.data["ad_group_ad_report"]["date"]
#         if record and record.type == Type.RECORD:
#             assert record.record.data["date"] >= current_state

#     # Abnormal state
#     state = "2029-06-04"
#     records = google_ads_client.read(AirbyteLogger(), SAMPLE_CONFIG, ConfiguredAirbyteCatalog.parse_obj(SAMPLE_CATALOG), {"ad_group_ad_report": {
#         "date": state
#     }})
#     current_state = (date.fromisoformat(state) -
#                      relativedelta(days=14)).isoformat()

#     no_records = True
#     for record in records:
#         if record and record.type == Type.STATE:
#             assert record.state.data["ad_group_ad_report"]["date"] == state
#         if record and record.type == Type.RECORD:
#             no_records = False

#     assert no_records == True
