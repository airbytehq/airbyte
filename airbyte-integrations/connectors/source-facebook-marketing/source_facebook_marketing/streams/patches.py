#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from urllib.parse import parse_qsl, urlparse, urlunparse

from facebook_business.api import Cursor

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException


logger = logging.getLogger("airbyte")


logger = logging.getLogger("airbyte")


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

        if not isinstance(response, dict):
            raise AirbyteTracedException(
                message="Facebook Marketing API response is not a JSON object.",
                internal_message=f"Expected dict from response_obj.json(), got {type(response).__name__}: {repr(response)[:200]}",
                failure_type=FailureType.transient_error,
            )

        paging = response.get("paging")
        if isinstance(paging, dict) and "next" in paging:
            path = paging["next"]
            # Here comes the magic.
            # self._path used to be path, self.params used to be {}
            # Now we separate params from the rest.
            self._path = urlunparse(urlparse(path)._replace(query={}))
            self.params = dict(parse_qsl(urlparse(path).query))
        else:
            if paging is not None and not isinstance(paging, dict):
                logger.warning(
                    "Facebook Marketing response had a non-dict 'paging' (%s); stopping pagination for this slice.",
                    type(paging).__name__,
                )
            self._finished_iteration = True

        summary = response.get("summary")
        if self._include_summary and isinstance(summary, dict) and "total_count" in summary:
            self._total_count = summary["total_count"]

        if self._include_summary and isinstance(summary, dict):
            self._summary = summary

        data = response.get("data")
        if isinstance(data, list):
            non_dict_count = sum(1 for item in data if not isinstance(item, dict))
            if non_dict_count:
                logger.warning("Filtered %d non-dict items from Facebook API response 'data' array.", non_dict_count)
                response["data"] = [item for item in data if isinstance(item, dict)]

        if isinstance(response.get("data"), list):
            valid_items = [item for item in response["data"] if isinstance(item, dict)]
            filtered_count = len(response["data"]) - len(valid_items)
            if filtered_count > 0:
                logger.warning(
                    "Filtered %d malformed (non-dict) item(s) from Meta API response in %s. "
                    "This is a known Meta API issue where string data is returned instead of objects.",
                    filtered_count,
                    self._path,
                )
                response = {**response, "data": valid_items}

        self._queue = self.build_objects_from_response(response)
        return len(self._queue) > 0
