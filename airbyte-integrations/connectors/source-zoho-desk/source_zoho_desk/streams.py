#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import concurrent.futures
import datetime
import math
from abc import ABC
from dataclasses import asdict
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream

from .api import ZohoAPI
from .exceptions import IncompleteMetaDataException, UnknownDataTypeException
from .types_zoho import FieldMeta, ModuleMeta, ZohoPickListItem

# 204 and 304 status codes are valid successful responses,
# but `.json()` will fail because the response body is empty
EMPTY_BODY_STATUSES = (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED)




class ZohoStreamFactory:
    def __init__(self, config: Mapping[str, Any]):
        self.api = ZohoAPI(config)
        self._config = config


    def _init_modules_meta(self) -> List[ModuleMeta]:
        modules_meta_json = self.api.modules_settings()
        modules = [ModuleMeta.from_dict(module) for module in modules_meta_json]
        return list(filter(lambda module: module, modules))
    
    
    def _populate_module_meta(self, module: ModuleMeta):
        module_meta_json = self.api.module_settings(module.api_name)
      
        module.update_from_dict(module_meta_json)

    
    def produce(self) -> List[HttpStream]:
        modules = self._init_modules_meta()
        streams = []
        def populate_module(module):
            self._populate_module_meta(module)

        def chunk(max_len, lst):
            for i in range(math.ceil(len(lst) / max_len)):
                yield lst[i * max_len : (i + 1) * max_len]

      
        max_concurrent_request = self.api.max_concurrent_requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_request) as executor:
            for batch in chunk(max_concurrent_request, modules):
                executor.map(lambda module: populate_module(module), batch)
        for module in modules:
            
            streams.append(module)
        
        return streams
    
        

    