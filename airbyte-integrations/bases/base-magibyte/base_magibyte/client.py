from typing import Tuple

from base_python import BaseClient


class MagibyteClient(BaseClient):
    def __init__(self, api_key):
        self._client = Harvest(api_key=api_key)
        super().__init__()

    def list(self, name, **kwargs):
        yield from paginator(getattr(self._client, name), **kwargs)

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {entity: partial(self.list, name=entity) for entity in self.ENTITIES}

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            # because there is no good candidate to try our connection
            # we use users endpoint as potentially smallest dataset
            self._client.users.get()
        except HTTPError as error:
            alive = False
            error_msg = str(error)

        return alive, error_msg
