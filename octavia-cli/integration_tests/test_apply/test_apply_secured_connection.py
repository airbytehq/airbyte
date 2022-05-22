import pytest

from octavia_cli.check_context import UnreachableAirbyteInstanceError
from octavia_cli.entrypoint import get_api_client


class TestSecuredEndpoint:

    def test_secured_source_and_destination(self, secured_source, destination_secured):
        assert not secured_source.was_created
        secured_source.create()
        secured_source.state = secured_source._get_state_from_file(secured_source.configuration_path)
        assert secured_source.was_created

        assert not destination_secured.was_created
        destination_secured.create()
        destination_secured.state = destination_secured._get_state_from_file(destination_secured.configuration_path)
        assert destination_secured.was_created

    def test_connection_secured(self, secured_source, destination_secured, connection_secured):
        assert secured_source.was_created
        assert destination_secured.was_created
        connection_secured.create()
        connection_secured.state = connection_secured._get_state_from_file(connection_secured.configuration_path)
        assert connection_secured.was_created

    def test_secured_api_endpoint_without_authentication(self):

        with pytest.raises(UnreachableAirbyteInstanceError):
            get_api_client("http://localhost:8010")


