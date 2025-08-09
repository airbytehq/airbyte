# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import List

from .base_requests_builder import MondayBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class BoardsRequestBuilder(MondayBaseRequestBuilder):
    @classmethod
    def boards_endpoint(cls, authenticator: Authenticator, board_ids: List[int] = None) -> "BoardsRequestBuilder":
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
            "query{boards(limit:10%s){id,name,board_kind,type,columns{archived,description,id,settings_str,title,type,width},communication,description,groups{archived,color,deleted,id,position,title},owners{id},creator{id},permissions,state,subscribers{id},tags{id},top_group{id},updated_at,updates{id},views{id,name,settings_str,type,view_specific_data_str},workspace{id,name,kind,description}}}"
            % board_ids_str
        )
        return params
