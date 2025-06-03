
import requests

from airbyte_cdk.sources.streams.http import HttpStream


class ExactStream(HttpStream):
    pass

    def test_access(self) -> bool:
        """Checks if the user has access to the specific API."""

        try:
            prepared_request = self._create_prepared_request(
                path=self.endpoint,
                headers=self._single_refresh_token_authenticator.get_auth_header(),
                # Just want to test if we can access the API, don't care about any results. With $top=0 we get no results.
                params={"$top": 0},
            )

            response = self._send_request(prepared_request, {})

            # Forbidden, user does not have access to the API
            if response.status_code == 401:
                return False

            response.raise_for_status()
            return True
        except requests.RequestException:
            return False