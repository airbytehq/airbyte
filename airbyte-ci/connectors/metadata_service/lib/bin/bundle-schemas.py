#!/usr/bin/env python3
"""
Bundle JSON schemas using Pydantic's schema() method.
This script generates a JSON schema from the generated Pydantic models.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import (
    ConnectorMetadataDefinitionV0,
)


def bundle_schemas():
    """Generate a bundled JSON schema from the Pydantic model."""
    try:
        print("📦 Bundling JSON schemas using Pydantic...")
        
        output_dir = Path(__file__).parent.parent / "metadata_service" / "models" / "generated"
        output_file = output_dir / "ConnectorMetadataDefinitionV0.json"
        
        print(f"   Output: {output_file}")
        
        schema = ConnectorMetadataDefinitionV0.schema()
        
        output_file.write_text(json.dumps(schema, indent=2))
        
        print(f"✅ Successfully bundled schema to {output_file}")
        print(f"   Schema contains {len(json.dumps(schema))} characters")
        
    except Exception as error:
        print(f"❌ Error bundling schemas: {error}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    bundle_schemas()
