from destination_netsuite.netsuite.configuration import Config
from destination_netsuite.netsuite.rest import NetSuiteRestApi
from destination_netsuite.netsuite import NetSuite

class RestBaseService:
    def __init__(self, path: str, config: Config):
        self._path=path
        self._ns = NetSuite(config)

    def __get_rest_api(self) -> NetSuiteRestApi:
        return self._ns.rest_api  # Cached property that initializes NetSuiteRestApi

    async def _get(self, subpath: str):
        rest_api=self.__get_rest_api()
        return await rest_api.get(subpath)

    async def _post(self, json: str):
        rest_api=self.__get_rest_api()
        return await rest_api.post(self._path, json=json)        

    async def add(self, json: str):
        return await self._post(json=json)

    async def get(self, request_path: str):
        subpath=self._path+request_path
        return await self._get(subpath=subpath)
    