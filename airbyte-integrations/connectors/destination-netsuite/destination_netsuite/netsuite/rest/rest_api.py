import logging
from typing import Sequence

from . import rest_api_base
from destination_netsuite.netsuite.configuration import Config, cached_property

__all__ = ("NetSuiteRestApi",)


class NetSuiteRestApi(rest_api_base.RestApiBase):
    def __init__(self, config: Config):
        self._config = config

    @cached_property
    def hostname(self) -> str:
        return self._make_hostname()

    async def get(self, subpath: str, **request_kw):
        return await self._request("GET", subpath, **request_kw)

    async def post(self, subpath: str, **request_kw):
        return await self._request("POST", subpath, **request_kw)

    async def put(self, subpath: str, **request_kw):
        return await self._request("PUT", subpath, **request_kw)

    async def patch(self, subpath: str, **request_kw):
        return await self._request("PATCH", subpath, **request_kw)

    async def delete(self, subpath: str, **request_kw):
        return await self._request("DELETE", subpath, **request_kw)

    def _make_hostname(self):
        return self._config.base_url

    def _make_url(self, subpath: str):
        return f"{self.hostname}/services/rest{subpath}"
