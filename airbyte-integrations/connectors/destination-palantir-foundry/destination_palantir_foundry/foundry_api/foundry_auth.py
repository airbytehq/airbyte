from foundry import ConfidentialClientAuth

from destination_palantir_foundry.config.foundry_config import FoundryConfig


class ConfidentialClientAuthFactory:
    def create(self, foundry_config: FoundryConfig, scopes: list[str]) -> ConfidentialClientAuth:
        return ConfidentialClientAuth(
            client_id=foundry_config.auth.client_id,
            client_secret=foundry_config.auth.client_secret,
            hostname=foundry_config.host,
            scopes=scopes
        )
