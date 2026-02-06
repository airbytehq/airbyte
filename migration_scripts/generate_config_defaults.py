"""Generate defaults.yaml files for connectors."""

from pathlib import Path
import yaml


def generate_config_file(connector_name: str, audit_result: dict, output_dir: Path):
    """
    Create defaults.yaml with non-secret config fields.

    Args:
        connector_name: e.g., "source-stripe"
        audit_result: Output from audit_connector()
        output_dir: e.g., connectors/source-stripe/
    """
    config_values = {}

    for secret in audit_result["secrets"]:
        raw_config = secret["raw_config"]
        config_field_names = secret["config_fields"]

        for field_name in config_field_names:
            if field_name in raw_config:
                config_values[field_name] = raw_config[field_name]

    config_file = output_dir / "defaults.yaml"
    with open(config_file, "w") as f:
        yaml.dump({"config": config_values}, f, default_flow_style=False)

    print(f"✓ Created {config_file}")
