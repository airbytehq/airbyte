# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import List

from .base_requests_builder import MondayBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class ItemsRequestBuilder(MondayBaseRequestBuilder):
    @classmethod
    def items_endpoint(cls, authenticator: Authenticator, board_ids: List[int] = None) -> "ItemsRequestBuilder":
        return cls().with_authenticator(authenticator).with_board_ids(board_ids)

    @property
    def query_params(self):
        params = super().query_params or {}
        if self._board_ids:
            board_ids = ", ".join(list(map(str, self._board_ids)))
            board_ids_str = f",ids:[{board_ids}]"
        else:
            board_ids_str = ""

        params["query"] = (
            "query{boards(limit:1%s){items_page(limit:20){cursor,items{id,name,assets{created_at,file_extension,file_size,id,name,original_geometry,public_url,uploaded_by{id},url,url_thumbnail},board{id,name},column_values{id,text,type,value,... on MirrorValue{display_value},... on BoardRelationValue{display_value},... on DependencyValue{display_value}},created_at,creator_id,group{id},parent_item{id},state,subscribers{id},updated_at,updates{id}}}}}"
            % board_ids_str
        )
        return params
