from abc import abstractmethod, ABC
from typing import Mapping, Any


class HttpAuthenticator(ABC):
    @abstractmethod
    def get_auth_header(self) -> Mapping[str, Any]:
        """
        :return: A dictionary containing all the necessary headers to authenticate.
        """


class NoAuth(HttpAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {}
