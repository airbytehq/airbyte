#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod


class Requester(ABC):
    @abstractmethod
    def get_authenticator(self):
        pass

    @abstractmethod
    def get_url_base(self):
        pass

    @abstractmethod
    def get_path(self):
        pass

    @abstractmethod
    def get_method(self):
        pass
