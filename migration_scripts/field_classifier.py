"""
Field classification for GSM to 1Password migration.

Determines whether fields are secrets or non-secret config based on field names only.
"""

import re
from dataclasses import dataclass
from enum import Enum


class FieldType(Enum):
    SECRET = "secret"
    CONFIG = "config"
    LOGIN = "login"  # Human login credentials (username/email + password)
    UNKNOWN = "unknown"


@dataclass
class ClassificationResult:
    field_name: str
    field_type: FieldType
    confidence: float  # 0.0 to 1.0
    reason: str


class FieldClassifier:
    """Classifies fields as secrets or config using field name patterns only."""

    # High-confidence regex patterns for secrets
    SECRET_PATTERNS = [
        # API credentials
        r"^api_?key$",
        r"^api_?secret$",
        r"^(access|refresh)_?token$",
        r"^(client|consumer)_?(secret|key)$",
        r"^private_?key$",
        r"^password$",
        r"^bearer_?token$",
        r"^auth_?token$",
        r"^secret_?key$",
        r"^webhook_?secret$",
        r"^signing_?secret$",
        # SSH/infrastructure keys
        r"^ssh_?key$",
        # Database infrastructure (sensitive)
        r"^database$",
        r"^tunnel_?host$",
        r"^tunnel_?port$",
        # Sensitive identifiers
        r"^account_?id$",
        r"^shop$",
        # Service infrastructure (hostnames, domains, instance URLs)
        r"^base_?url$",
        r"^domain$",
        # Database connection details
        r"^host$",
        r"^port$",
    ]

    # High-confidence regex patterns for config
    CONFIG_PATTERNS = [
        # URLs/URIs (except base_url which is infrastructure)
        r"^redirect_?uri$",
        r"^api_?url$",
        r"^endpoint$",
        # Dates and time ranges
        r"^.*_date$",
        r"^lookback_?window$",
        r"^slice_?range$",
        r"^bulk_?window_?in_?days$",
        r"^initial_?waiting_?seconds$",
        # Non-sensitive identifiers (public OAuth client IDs, etc.)
        r"^client_?id$",  # Public OAuth client identifier
        # Geographic/organizational
        r"^region$",
        r"^subdomain$",
        r"^workspace$",
        r"^tenant$",
        r"^organization$",
        # Method/type configuration
        r"^.*_method$",  # auth_method, tunnel_method, replication_method
        r"^.*_type$",    # auth_type, api_type
        r"^method$",     # Innermost name from nested method fields
        # Boolean flags and feature toggles
        r"^is_.*$",       # is_sandbox, is_test
        r"^enable_.*$",   # enable_experimental_streams
        r"^join_.*$",     # join_channels
        r"^fetch_.*$",    # fetch_transactions_user_id
        r"^tls$",
        r"^ssl_?mode$",
        # CDC/replication configuration
        r"^plugin$",
        r"^replication_?slot$",
        r"^publication$",
        # Pagination and sizing
        r"^_?page_?size$",
        # Lists and collections (non-sensitive)
        r"^projects$",
        r"^repository$",
        r"^repositories$",
        r"^channel_?filter$",
        r"^streams_?criteria$",
        # Test configuration
        r"^object_?ids$",
        # SSH tunnel configuration metadata (not credentials)
        r"^tunnel_?user$",
    ]

    # High-confidence patterns for login credentials (username/email)
    LOGIN_PATTERNS = [
        r"^username$",
        r"^user_name$",
        r"^email$",
        r"^user_email$",
        r"^login$",
        r"^login_email$",
        r"^account_email$",
    ]

    # Keywords suggesting secret (lower confidence - require full match)
    SECRET_KEYWORDS = [
        "secret", "password", "token", "private", "key",
        "credential", "auth", "bearer", "signature"
    ]

    # Built from Phase 1a cross-connector analysis
    # Populated by analyze_all_connectors() - fields appearing in 10+ connectors
    CONFIG_ALLOWLIST = set()

    # Explicit overrides from manual review
    SECRET_BLOCKLIST = {
        "shared_secret", "app_token", "service_token",
        "webhook_signing_secret", "hmac_key"
    }

    def classify(self, field_name: str, field_value: any = None) -> ClassificationResult:
        """Classify a field as secret, config, or unknown based on field name."""
        field_lower = field_name.lower()

        # 1. Check explicit overrides first
        if field_lower in self.CONFIG_ALLOWLIST:
            return ClassificationResult(
                field_name, FieldType.CONFIG, 1.0,
                "Global config allowlist (from Phase 1a analysis)"
            )

        if field_lower in self.SECRET_BLOCKLIST:
            return ClassificationResult(
                field_name, FieldType.SECRET, 1.0,
                "Global secret blocklist"
            )

        # 2. Check high-confidence LOGIN patterns
        for pattern in self.LOGIN_PATTERNS:
            if re.match(pattern, field_lower):
                return ClassificationResult(
                    field_name, FieldType.LOGIN, 0.95,
                    f"Login credential pattern match: {pattern}"
                )

        # 3. Check high-confidence SECRET patterns
        for pattern in self.SECRET_PATTERNS:
            if re.match(pattern, field_lower):
                return ClassificationResult(
                    field_name, FieldType.SECRET, 0.95,
                    f"Secret pattern match: {pattern}"
                )

        # 4. Check high-confidence CONFIG patterns
        for pattern in self.CONFIG_PATTERNS:
            if re.match(pattern, field_lower):
                return ClassificationResult(
                    field_name, FieldType.CONFIG, 0.95,
                    f"Config pattern match: {pattern}"
                )

        # 5. Check secret keywords (lower confidence)
        matched_keywords = [kw for kw in self.SECRET_KEYWORDS if kw in field_lower]
        if matched_keywords:
            confidence = min(0.7 + (len(matched_keywords) * 0.1), 0.9)
            return ClassificationResult(
                field_name, FieldType.SECRET, confidence,
                f"Secret keyword match: {', '.join(matched_keywords)}"
            )

        # 6. Very limited value-based detection (only extremely specific patterns)
        if field_value is not None and isinstance(field_value, str):
            # JWT: exactly 3 base64 segments separated by dots
            if field_value.count('.') == 2 and len(field_value) > 50:
                parts = field_value.split('.')
                if all(re.match(r'^[A-Za-z0-9_-]+$', p) for p in parts):
                    return ClassificationResult(
                        field_name, FieldType.SECRET, 0.9,
                        "JWT format detected"
                    )

            # PEM format
            if field_value.startswith('-----BEGIN'):
                return ClassificationResult(
                    field_name, FieldType.SECRET, 0.95,
                    "PEM format detected"
                )

        # 7. Unknown - REQUIRE manual review (no guessing)
        return ClassificationResult(
            field_name, FieldType.UNKNOWN, 0.0,
            "No pattern match - manual review required"
        )
