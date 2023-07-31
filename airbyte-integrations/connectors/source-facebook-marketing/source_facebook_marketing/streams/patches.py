#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qsl, urlparse, urlunparse

from facebook_business.api import Cursor


class CursorPatch(Cursor):
    """
    This is a hack to override FB SDK Cursor's default behaviour. By default, api calls are made using signature
    def call(
        self,
        method,
        path,
        params=None,
        headers=None,
        files=None,
        url_override=None,
        api_version=None,
    )
    If the call fails with a `Please reduce the amount of data you're asking for, then retry your request` message,
    we try to decrease the limit by 2 in the retry handler if it is passed in the `params`.
    The tricky thing is that the `limit` option is passed in the `params` only for the first page. Further pages are fetched passing the
    whole URL in the `path` param. To change this, the `load_next_page` method was overridden where the params are separated from the path.
    """

    def load_next_page(self):
        """Queries server for more nodes and loads them into the internal queue.
        Returns:
            True if successful, else False.
        """
        if self._finished_iteration:
            return False

        if self._include_summary and "default_summary" not in self.params and "summary" not in self.params:
            self.params["summary"] = True

        response_obj = self._api.call(
            "GET",
            self._path,
            params=self.params,
        )
        response = response_obj.json()
        self._headers = response_obj.headers()

        if "paging" in response and "next" in response["paging"]:
            path = response["paging"]["next"]
            # Here comes the magic.
            # self._path used to be path, self.params used to be {}
            # Now we separate params from the rest.
            self._path = urlunparse(urlparse(path)._replace(query={}))
            self.params = dict(parse_qsl(urlparse(path).query))
        else:
            # Indicate if this was the last page
            self._finished_iteration = True

        if self._include_summary and "summary" in response and "total_count" in response["summary"]:
            self._total_count = response["summary"]["total_count"]

        if self._include_summary and "summary" in response:
            self._summary = response["summary"]

        self._queue = self.build_objects_from_response(response)
        return len(self._queue) > 0
