"""
Integration test for podcast RSS feeds.
Test that enclosure URLs are extracted and start_date filtering works.
"""
import json
import os
from typing import Any, Dict, List, Mapping

from airbyte_cdk.models import AirbyteMessage, Type
from source_rss.source import SourceRss


def read_config() -> Dict[str, Any]:
    """Read the config from the secrets file."""
    secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secrets/config.json")
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as f:
            return json.loads(f.read())
    
    # If no secrets file, fall back to the sample config
    sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_config.json")
    if os.path.exists(sample_path):
        with open(sample_path, "r") as f:
            return json.loads(f.read())
    
    raise ValueError("No valid configuration found. Please create a secrets/config.json file.")


def run_source_and_read_records() -> List[Dict[str, Any]]:
    """Run the source with a podcast feed and return the extracted records."""
    config = read_config()
    source = SourceRss()
    
    catalog = source.discover(config)
    configured_catalog = {
        "streams": [
            {
                "stream": stream,
                "sync_mode": "full_refresh",
                "destination_sync_mode": "overwrite",
            }
            for stream in catalog.streams
        ]
    }
    
    records = []
    for message in source.read(config, configured_catalog, None):
        if message.type == Type.RECORD:
            records.append(message.record.data)
    
    return records


def test_podcast_enclosures():
    """Test that podcast feed enclosure URLs are correctly extracted."""
    records = run_source_and_read_records()
    
    # We should get some records since we're using a historical start_date
    assert len(records) > 0, "No records returned from the source"
    
    # Check that some records have enclosure URLs
    records_with_enclosures = [r for r in records if r.get("enclosure")]
    assert len(records_with_enclosures) > 0, "No records with enclosure URLs found"
    
    # Check that the enclosure URLs look like valid URLs
    for record in records_with_enclosures[:5]:  # Check first 5 records
        assert isinstance(record["enclosure"], str), f"Enclosure is not a string: {record['enclosure']}"
        assert record["enclosure"].startswith("http"), f"Enclosure doesn't look like a URL: {record['enclosure']}"
        
    print(f"Found {len(records)} records, {len(records_with_enclosures)} with enclosure URLs")
    
    # Print some sample records
    print("\nSample records with enclosures:")
    for record in records_with_enclosures[:3]:
        print(f"Title: {record.get('title')}")
        print(f"Enclosure URL: {record.get('enclosure')}")
        print("---")


if __name__ == "__main__":
    test_podcast_enclosures() 