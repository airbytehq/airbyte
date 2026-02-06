"""
GSM to 1Password Migration Script.

Usage:
    python gsm_to_1password.py --connector source-stripe --dry-run
    python gsm_to_1password.py --connector source-stripe --execute
"""

import subprocess
import json
import hashlib
from dataclasses import dataclass
from pathlib import Path
from naming_utils import extract_root_name


@dataclass
class MigrationResult:
    connector: str
    status: str
    sections_created: list[str]
    fields_migrated: int
    error: str | None = None


class OnePasswordMigrator:
    """Migrates GSM secrets to 1Password."""

    VAULT = "replication-connector-credentials"
    SECTION_PREFIX = "test-credentials-"

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self._verify_op_cli()

    def _verify_op_cli(self) -> None:
        result = subprocess.run(
            ["op", "account", "list", "--format=json"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError("1Password CLI not authenticated.")

    def _item_exists(self, item_name: str) -> bool:
        result = subprocess.run(
            ["op", "item", "get", item_name, "--vault", self.VAULT, "--format=json"],
            capture_output=True, text=True,
        )
        return result.returncode == 0

    def _run_op_command(self, cmd: list[str]) -> tuple[bool, str]:
        if self.dry_run:
            # SECURITY: Never log the full command as it contains secret values
            # Only log the operation type
            operation = cmd[1] if len(cmd) > 1 else "unknown"
            item_name = cmd[3] if len(cmd) > 3 and operation == "create" else (cmd[2] if len(cmd) > 2 else "unknown")
            return True, f"[DRY RUN] Would execute: op {operation} {item_name} [REDACTED]"
        result = subprocess.run(cmd, capture_output=True, text=True)
        return (result.returncode == 0, result.stdout if result.returncode == 0 else result.stderr)

    def migrate_connector(self, connector_name: str, gsm_secrets: list[dict]) -> MigrationResult:
        """
        Migrate connector from GSM to 1Password.

        Args:
            connector_name: Full connector name (e.g., "source-stripe")
            gsm_secrets: List of GSM secrets with audit results

        Note:
            1Password items are created using root names (e.g., "stripe")
        """
        # Extract root name for 1Password item (source-stripe -> stripe)
        item_name = extract_root_name(connector_name)

        variants, login_sections = self._group_by_variant(gsm_secrets)

        # Print deduplication warnings if any
        if hasattr(self, '_dedup_warnings') and self._dedup_warnings:
            for warning in self._dedup_warnings:
                print(f"\n{warning}")

        if self._item_exists(item_name):
            return self._update_item(item_name, variants, login_sections)
        return self._create_item(item_name, variants, login_sections)

    def _normalize_field_name(self, field_name: str) -> str:
        """
        Normalize field names for 1Password storage.

        Removes flattening prefixes and renames to canonical names.

        Examples:
            credentials_personal_access_token → token
            credentials_access_token → token
            credentials_api_url → api_url (but this is config, won't reach here)
        """
        # Remove common prefixes from flattened nested structures
        if field_name.startswith("credentials_"):
            field_name = field_name[len("credentials_"):]

        # Normalize token field names
        if field_name in ["personal_access_token", "access_token", "bearer_token"]:
            return "token"

        return field_name

    def _calculate_auth_fingerprint(self, auth_data: dict) -> str:
        """Calculate fingerprint from auth fields only (for deduplication)."""
        if not auth_data:
            return ""
        # Sort keys for consistent fingerprinting
        sorted_items = sorted(auth_data.items())
        auth_string = json.dumps(sorted_items, sort_keys=True)
        return hashlib.sha256(auth_string.encode()).hexdigest()[:12]

    def _group_by_variant(self, secrets: list[dict]) -> tuple[dict[str, dict], dict]:
        """
        Group secrets by auth variant with credential deduplication.

        Deduplication strategy:
        - Auth fields: Deduplicated by fingerprint (same credentials stored once)
        - Config fields: NOT deduplicated (all variants preserved)
        - Login fields: Support multiple login sections with variant suffixes

        Args:
            secrets: List of dicts with structure from audit_connector():
                {
                    "secret_name": str,
                    "raw_config": dict,  # Full JSON blob from GSM
                    "auth_fields": list[str],  # Field names classified as secrets
                    "config_fields": list[str],  # Field names classified as config
                    "login_fields": list[str],  # Field names for login credentials
                    "variant": str  # Inferred variant name
                }

        Returns:
            Tuple of (variants_dict, login_sections_dict):
            variants_dict: {
                "oauth": {"auth": {"client_id": "...", ...}, "config": {"account_id": ...}},
                "backup": {"auth": {}, "config": {"account_id": ...}},  # auth empty if duplicate
            }
            login_sections_dict: {
                "login": {"username": "...", "password": "..."},
                "login-test-user-2": {"username": "...", "password": "..."}
            }
        """
        variants: dict[str, dict] = {}
        login_sections: dict[str, dict] = {}
        auth_fingerprints: dict[str, str] = {}  # fingerprint -> variant_name mapping
        self._dedup_warnings = []  # Track warnings for preview/output

        for secret in secrets:
            variant = secret.get("variant", self._infer_variant(secret))
            if variant not in variants:
                variants[variant] = {"auth": {}, "config": {}}

            raw_config = secret["raw_config"]
            auth_field_names = secret.get("auth_fields", [])
            config_field_names = secret.get("config_fields", [])
            login_field_names = secret.get("login_fields", [])

            # Extract auth field values
            auth_data = {
                field_name: raw_config[field_name]
                for field_name in auth_field_names
                if field_name in raw_config
            }

            # Check for duplicate credentials by fingerprint
            if auth_data:
                fingerprint = self._calculate_auth_fingerprint(auth_data)
                if fingerprint in auth_fingerprints:
                    # Duplicate credentials found - skip storing auth, but keep config
                    existing_variant = auth_fingerprints[fingerprint]
                    self._dedup_warnings.append(
                        f"⚠️  Duplicate credentials in variant '{variant}' "
                        f"(same as '{existing_variant}'). "
                        f"Reusing credentials from '{existing_variant}', storing config separately."
                    )
                else:
                    # New credentials - store them
                    auth_fingerprints[fingerprint] = variant
                    variants[variant]["auth"] = auth_data

            # Always store config fields (no deduplication)
            for field_name in config_field_names:
                if field_name in raw_config:
                    variants[variant]["config"][field_name] = raw_config[field_name]

            # Handle login credentials with variant-specific sections
            if login_field_names:
                login_data = {
                    field_name: raw_config[field_name]
                    for field_name in login_field_names
                    if field_name in raw_config
                }
                if login_data:
                    # Use variant name for login section if not default
                    login_section_name = "login" if variant == "default" else f"login-{variant}"

                    # Check if this login section already has data
                    if login_section_name in login_sections:
                        # Check if it's a duplicate
                        existing_fingerprint = self._calculate_auth_fingerprint(login_sections[login_section_name])
                        new_fingerprint = self._calculate_auth_fingerprint(login_data)
                        if existing_fingerprint != new_fingerprint:
                            self._dedup_warnings.append(
                                f"⚠️  Multiple different login credentials found for variant '{variant}'. "
                                f"Last value will be used."
                            )

                    login_sections[login_section_name] = login_data

        return variants, login_sections

    def _extract_variant_from_secret_name(self, secret_name: str) -> str | None:
        """
        Extract variant suffix from GSM secret name.

        Examples:
        - SECRET_SOURCE-STRIPE__CREDS → None (use default inference)
        - SECRET_SOURCE-STRIPE_OAUTH__CREDS → "oauth"
        - SECRET_SOURCE-STRIPE_BACKUP__CREDS → "backup"
        - SECRET_SOURCE-STRIPE_TEST-USER-1__CREDS → "test-user-1"
        """
        # Remove SECRET_ prefix and __CREDS suffix
        name = secret_name.upper()
        if name.startswith("SECRET_"):
            name = name[7:]  # Remove "SECRET_"
        if "__CREDS" in name:
            name = name.split("__CREDS")[0]

        # Split by underscore to find suffix after connector name
        # Format: SOURCE-STRIPE_SUFFIX or DESTINATION-MYSQL_SUFFIX
        parts = name.split("_")
        if len(parts) > 1:
            # Last part is the suffix
            suffix = parts[-1].lower().replace("_", "-")
            return suffix
        return None

    def _infer_variant(self, secret: dict) -> str:
        """
        Infer auth variant from secret name and auth field names.

        Priority:
        1. Explicit variant suffix in secret name (e.g., _OAUTH, _BACKUP)
        2. Known auth patterns in secret name (oauth, api-key, service-account)
        3. Field name patterns (e.g., client_id → oauth)
        4. Default to "default"
        """
        name = secret.get("secret_name", "")
        auth_fields = secret.get("auth_fields", [])

        # Try to extract variant from secret name suffix first
        variant_suffix = self._extract_variant_from_secret_name(name)
        if variant_suffix:
            # Check if it's a known auth type
            if variant_suffix in ["oauth", "api-key", "service-account", "basic"]:
                return variant_suffix
            # Otherwise use the suffix as-is (e.g., "backup", "test-user-1")
            # But still check for known patterns to override generic suffixes
            name_lower = name.lower()
            if "oauth" in name_lower and variant_suffix not in ["backup", "test", "prod", "dev"]:
                return "oauth"
            if "service_account" in name_lower or "service-account" in name_lower:
                return "service-account"
            if "api_key" in name_lower or "api-key" in name_lower:
                return "api-key"
            if "basic" in name_lower:
                return "basic"
            # Use the extracted suffix
            return variant_suffix

        # No suffix found - check secret name for known patterns
        name_lower = name.lower()
        if "oauth" in name_lower:
            return "oauth"
        if "service_account" in name_lower or "service-account" in name_lower:
            return "service-account"
        if "api_key" in name_lower or "api-key" in name_lower:
            return "api-key"
        if "basic" in name_lower:
            return "basic"

        # Infer from auth field names
        field_names = set(auth_fields)
        if "client_id" in field_names or "client_secret" in field_names:
            return "oauth"
        if "private_key" in field_names or "service_account_key" in field_names:
            return "service-account"
        if "api_key" in field_names:
            return "api-key"
        if "username" in field_names and "password" in field_names:
            return "basic"

        return "default"

    def _create_item(self, connector_name: str, variants: dict[str, dict],
                     login_sections: dict[str, dict]) -> MigrationResult:
        """
        Create 1Password item with secret auth fields and login credentials.

        SECURITY: Config fields are NOT migrated to 1Password - they go to repo files.

        Args:
            connector_name: Root connector name (e.g., "stripe")
            variants: Dict of variants with auth/config data
            login_sections: Dict of login section names to credential data
        """
        cmd = ["op", "item", "create", "--category", "Secure Note",
               "--title", connector_name, "--vault", self.VAULT, "--format", "json"]

        sections_created = []
        fields_migrated = 0

        # Add test-credentials-{variant} sections for API auth (only if auth fields exist)
        for variant_name, variant_data in variants.items():
            if variant_data["auth"]:  # Only create section if there are auth fields
                section = f"{self.SECTION_PREFIX}{variant_name}"
                sections_created.append(section)

                # ONLY migrate auth (secret) fields to 1Password
                for field, value in variant_data["auth"].items():
                    # Normalize field name for cleaner 1Password storage
                    normalized_field = self._normalize_field_name(field)
                    cmd.append(f"{section}.{normalized_field}[password]={value}")
                    fields_migrated += 1

            # Config fields are skipped - they go to defaults.yaml in repo

        # Add login sections for human credentials (if present)
        for login_section_name, login_data in login_sections.items():
            sections_created.append(login_section_name)
            for field, value in login_data.items():
                # Password fields are secret, username/email are text
                field_type = "password" if field == "password" else "text"
                cmd.append(f"{login_section_name}.{field}[{field_type}]={value}")
                fields_migrated += 1

        success, output = self._run_op_command(cmd)
        return MigrationResult(
            connector=connector_name,
            status="created" if success else "failed",
            sections_created=sections_created,
            fields_migrated=fields_migrated,
            error=output if not success else None,
        )

    def _update_item(self, connector_name: str, variants: dict[str, dict],
                     login_sections: dict[str, dict]) -> MigrationResult:
        """
        Update existing 1Password item with secret auth fields and login credentials.

        SECURITY: Config fields are NOT migrated to 1Password - they go to repo files.

        Args:
            connector_name: Root connector name (e.g., "stripe")
            variants: Dict of variants with auth/config data
            login_sections: Dict of login section names to credential data
        """
        sections_created = []
        fields_migrated = 0

        # Update test-credentials-{variant} sections for API auth (only if auth fields exist)
        for variant_name, variant_data in variants.items():
            if variant_data["auth"]:  # Only create section if there are auth fields
                section = f"{self.SECTION_PREFIX}{variant_name}"
                sections_created.append(section)

                # ONLY migrate auth (secret) fields to 1Password
                for field, value in variant_data["auth"].items():
                    # Normalize field name for cleaner 1Password storage
                    normalized_field = self._normalize_field_name(field)
                    cmd = ["op", "item", "edit", connector_name, "--vault", self.VAULT,
                           f"{section}.{normalized_field}[password]={value}"]
                    success, _ = self._run_op_command(cmd)
                    if success:
                        fields_migrated += 1

            # Config fields are skipped - they go to defaults.yaml in repo

        # Update login sections for human credentials (if present)
        for login_section_name, login_data in login_sections.items():
            sections_created.append(login_section_name)
            for field, value in login_data.items():
                # Password fields are secret, username/email are text
                field_type = "password" if field == "password" else "text"
                cmd = ["op", "item", "edit", connector_name, "--vault", self.VAULT,
                       f"{login_section_name}.{field}[{field_type}]={value}"]
                success, _ = self._run_op_command(cmd)
                if success:
                    fields_migrated += 1

        return MigrationResult(
            connector=connector_name, status="updated",
            sections_created=sections_created, fields_migrated=fields_migrated,
        )

    def generate_preview(self, connector_name: str, gsm_secrets: list[dict]) -> str:
        """
        Generate a preview of the 1Password migration with deduplication info.

        Args:
            connector_name: Full connector name (e.g., "source-stripe")
            gsm_secrets: Audit results from audit_connector()
        """
        # Extract root name for 1Password item
        item_name = extract_root_name(connector_name)

        variants, login_sections = self._group_by_variant(gsm_secrets)
        lines = [f"=== Migration Preview for {connector_name} ===",
                 f"Vault: {self.VAULT}", f"Item: {item_name}", ""]

        # Show deduplication warnings if any
        if hasattr(self, '_dedup_warnings') and self._dedup_warnings:
            for warning in self._dedup_warnings:
                lines.append(warning)
            lines.append("")

        # Show test-credentials-{variant} sections (ONLY auth fields go to 1Password)
        for variant_name, variant_data in variants.items():
            section = f"{self.SECTION_PREFIX}{variant_name}"
            if variant_data["auth"]:
                lines.append(f"├── Section: {section}")
                for field in variant_data["auth"].keys():
                    # Show normalized field name that will be used in 1Password
                    normalized_field = self._normalize_field_name(field)
                    lines.append(f"│   ├── {normalized_field} [password]")
            else:
                # Variant exists but has no auth fields (duplicate credentials)
                lines.append(f"├── Section: {section} (credentials reused, no new fields)")

        # Show login sections (if present)
        for login_section_name, login_data in login_sections.items():
            lines.append(f"├── Section: {login_section_name}")
            for field in login_data.keys():
                field_type = "password" if field == "password" else "text"
                lines.append(f"│   ├── {field} [{field_type}]")

        # Show config fields grouped by variant (goes to repo, NOT 1Password)
        lines.append("")
        lines.append("Config fields (NOT in 1Password, goes to repo defaults.yaml):")
        for variant_name, variant_data in variants.items():
            if variant_data["config"]:
                lines.append(f"  {variant_name}:")
                for field, value in variant_data["config"].items():
                    # Show a preview of the value (truncated for security)
                    value_preview = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                    lines.append(f"    - {field}: {value_preview}")

        return "\n".join(lines)
