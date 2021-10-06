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


from airbyte_cdk.models import AirbyteCatalog, AirbyteStream, SyncMode
from airbyte_cdk.sources.utils.catalog_helpers import CatalogHelper


def test_coerce_catalog_as_full_refresh():
    incremental = AirbyteStream(
        name="1",
        json_schema={"k": "v"},
        supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh],
        source_defined_cursor=True,
        default_cursor_field=["cursor"],
    )
    full_refresh = AirbyteStream(
        name="2", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh], source_defined_cursor=False
    )
    input = AirbyteCatalog(streams=[incremental, full_refresh])

    expected = AirbyteCatalog(
        streams=[
            AirbyteStream(name="1", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh], source_defined_cursor=False),
            full_refresh,
        ]
    )

    assert expected == CatalogHelper.coerce_catalog_as_full_refresh(input)
