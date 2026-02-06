"""
Credential loader for Coral connectors with dual-read support.

Supports loading from 1Password with GSM fallback during transition.
"""

from pathlib import Path
import yaml
import json
import subprocess
from naming_utils import extract_root_name


class OnePasswordClient:
    """Wrapper for 1Password CLI operations."""

    def __init__(self, vault: str):
        self.vault = vault

    def get_item(self, item_name: str) -> dict:
        """Get 1Password item by name."""
        result = subprocess.run(
            ["op", "item", "get", item_name, "--vault", self.vault, "--format=json"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to get 1Password item: {item_name}")
        return json.loads(result.stdout)


class CoralCredentialLoader:
    """Loads credentials for Coral connectors with fallback."""

    def __init__(self, enable_gsm_fallback: bool = True):
        self.op_client = OnePasswordClient(vault="replication-connector-credentials")
        self.enable_gsm_fallback = enable_gsm_fallback

    def load_credentials(self, connector_name: str, gsm_credentials: dict = None) -> dict:
        """
        Load credentials with dual-read fallback.

        Priority:
        1. Load config defaults from repo
        2. Try 1Password for secrets
        3. If 1Password fails and fallback enabled, try GSM
        4. Merge and return

        Args:
            connector_name: Full name (e.g., "source-stripe")
            gsm_credentials: GSM credentials (required if fallback enabled)

        Returns:
            Merged config dict with secrets and non-secrets
        """
        # Load config defaults from repo
        config = self._load_defaults(connector_name)

        # Try 1Password first
        try:
            secrets = self._load_from_1password(connector_name)
            config.update(secrets)
            print(f"✓ Loaded credentials from 1Password: {connector_name}")
            return config
        except Exception as e:
            print(f"⚠️  1Password load failed: {e}")

            # Fallback to GSM if enabled
            if self.enable_gsm_fallback and gsm_credentials:
                print(f"→ Falling back to GSM for {connector_name}")
                secrets = self._load_from_gsm(connector_name, gsm_credentials)
                config.update(secrets)
                return config
            else:
                raise RuntimeError(f"Failed to load credentials for {connector_name}")

    def _load_defaults(self, connector_name: str) -> dict:
        """Load non-secret config from repository."""
        defaults_file = Path(f"connectors/{connector_name}/defaults.yaml")
        if defaults_file.exists():
            with open(defaults_file) as f:
                data = yaml.safe_load(f)
                return data.get("config", {})
        return {}

    def _load_from_1password(self, connector_name: str) -> dict:
        """
        Load secrets from 1Password.

        Args:
            connector_name: Full connector name (e.g., "source-stripe")

        Note:
            Extracts root name (e.g., "stripe") for 1Password item lookup
        """
        # Extract root name for 1Password lookup (source-stripe -> stripe)
        item_name = extract_root_name(connector_name)
        item = self.op_client.get_item(item_name)

        secrets = {}
        for field in item.get("fields", []):
            section = field.get("section", {}).get("label", "")
            # Only load from test-credentials-* sections
            if section.startswith("test-credentials-"):
                field_name = field.get("label")
                field_value = field.get("value")
                if field_name and field_value:
                    secrets[field_name] = field_value

        return secrets

    def _load_from_gsm(self, connector_name: str, gsm_credentials: dict) -> dict:
        """Load secrets from GSM (fallback)."""
        from ci_credentials.secrets_manager import SecretsManager

        manager = SecretsManager(connector_name, gsm_credentials)
        secrets = manager.read_from_gsm()

        # Merge all GSM secrets (flatten)
        merged = {}
        for secret in secrets:
            config = json.loads(secret.value)
            merged.update(config)

        return merged
