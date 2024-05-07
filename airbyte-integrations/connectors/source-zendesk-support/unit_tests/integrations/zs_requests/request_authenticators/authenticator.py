# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import abc


class Authenticator(abc.ABC):
    @abc.abstractproperty
    def client_access_token(self) -> str:
        """"""
