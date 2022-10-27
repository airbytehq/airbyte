from unittest.mock import Mock, MagicMock


class MockGoogleAdManagerAuthenticator:

    def __init__(self):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True
    generate_report_downloader = Mock(return_value=None)
    get_networks = Mock(return_value=None)
    set_network = Mock(return_value=None)
    get_client = Mock(return_value=None)
