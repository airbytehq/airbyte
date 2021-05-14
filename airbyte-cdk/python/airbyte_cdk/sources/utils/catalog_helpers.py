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


from airbyte_cdk.models import AirbyteCatalog, SyncMode


class CatalogHelper:
    @staticmethod
    def coerce_catalog_as_full_refresh(catalog: AirbyteCatalog) -> AirbyteCatalog:
        """
        Updates the sync mode on all streams in this catalog to be full refresh
        """
        coerced_catalog = catalog.copy()
        for stream in catalog.streams:
            stream.source_defined_cursor = False
            stream.supported_sync_modes = [SyncMode.full_refresh]
            stream.default_cursor_field = None

        # remove nulls
        return AirbyteCatalog.parse_raw(coerced_catalog.json(exclude_unset=True, exclude_none=True))
