#!/usr/bin/env python3
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Detect interleaved streams in Airbyte connectors by analyzing manifest.yaml files
for SubstreamPartitionRouter patterns and generating metadata.yaml extensions.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml


class InterleavedStreamDetector:
    """Detects and analyzes interleaved stream patterns in Airbyte connectors."""

    def __init__(self, connectors_path: str):
        self.connectors_path = Path(connectors_path)
        self.results = {}

    def scan_all_connectors(self) -> Dict[str, Any]:
        """Scan all connectors for interleaved stream patterns."""
        results = {}

        for connector_dir in self.connectors_path.iterdir():
            if not connector_dir.is_dir() or not connector_dir.name.startswith(("source-", "destination-")):
                continue

            manifest_path = connector_dir / "manifest.yaml"
            if not manifest_path.exists():
                continue

            try:
                connector_results = self.analyze_connector(connector_dir)
                if connector_results["interleaved_streams"]:
                    results[connector_dir.name] = connector_results
            except Exception as e:
                print(f"Error analyzing {connector_dir.name}: {e}", file=sys.stderr)

        return results

    def analyze_connector(self, connector_dir: Path) -> Dict[str, Any]:
        """Analyze a single connector for interleaved stream patterns."""
        manifest_path = connector_dir / "manifest.yaml"
        metadata_path = connector_dir / "metadata.yaml"

        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)

        existing_metadata = {}
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                existing_metadata = yaml.safe_load(f)

        interleaved_streams = self.detect_substream_patterns(manifest)
        performance_indicators = self.detect_performance_indicators(manifest)

        documented_streams = self.get_documented_interleaved_streams(existing_metadata)

        return {
            "connector_name": connector_dir.name,
            "manifest_path": str(manifest_path),
            "metadata_path": str(metadata_path),
            "interleaved_streams": interleaved_streams,
            "performance_indicators": performance_indicators,
            "documented_streams": documented_streams,
            "needs_documentation": bool(interleaved_streams and not documented_streams),
            "has_performance_flags": bool(performance_indicators),
        }

    def detect_substream_patterns(self, manifest: Dict[str, Any]) -> List[List[str]]:
        """Detect SubstreamPartitionRouter patterns and build interleaved stream lists."""
        interleaved_groups = []
        stream_definitions = manifest.get("definitions", {}).get("streams", {})

        relationships = {}  # child -> [parents]

        for stream_name, stream_config in stream_definitions.items():
            parents = self.extract_parent_streams(stream_config)
            if parents:
                relationships[stream_name] = parents

        processed = set()

        for child_stream, parent_streams in relationships.items():
            if child_stream in processed:
                continue

            group = self.build_dependency_chain(child_stream, relationships, stream_definitions)
            if len(group) > 1:  # Only include groups with actual dependencies
                interleaved_groups.append(sorted(group))
                processed.update(group)

        return interleaved_groups

    def extract_parent_streams(self, stream_config: Dict[str, Any]) -> List[str]:
        """Extract parent stream names from a stream configuration."""
        parents = []

        def find_substream_routers(config: Any) -> None:
            if isinstance(config, dict):
                if config.get("type") == "SubstreamPartitionRouter":
                    parent_configs = config.get("parent_stream_configs", [])
                    for parent_config in parent_configs:
                        stream_ref = parent_config.get("stream", "")
                        if isinstance(stream_ref, str) and stream_ref.startswith("#/definitions/streams/"):
                            parent_name = stream_ref.split("/")[-1]
                            parents.append(parent_name)
                        elif isinstance(stream_ref, dict) and "$ref" in stream_ref:
                            ref = stream_ref["$ref"]
                            if ref.startswith("#/definitions/streams/"):
                                parent_name = ref.split("/")[-1]
                                parents.append(parent_name)

                for value in config.values():
                    find_substream_routers(value)
            elif isinstance(config, list):
                for item in config:
                    find_substream_routers(item)

        find_substream_routers(stream_config)
        return list(set(parents))  # Remove duplicates

    def build_dependency_chain(
        self, start_stream: str, relationships: Dict[str, List[str]], stream_definitions: Dict[str, Any], visited: Set[str] = None
    ) -> Set[str]:
        """Build a complete dependency chain starting from a stream."""
        if visited is None:
            visited = set()

        if start_stream in visited:
            return {start_stream}  # Avoid infinite recursion

        visited.add(start_stream)
        chain = {start_stream}

        if start_stream in relationships:
            for parent in relationships[start_stream]:
                chain.update(self.build_dependency_chain(parent, relationships, stream_definitions, visited.copy()))

        for child, parents in relationships.items():
            if start_stream in parents:
                chain.update(self.build_dependency_chain(child, relationships, stream_definitions, visited.copy()))

        return chain

    def detect_performance_indicators(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Detect performance-related indicators in the manifest."""
        indicators = {"incremental_dependency_streams": [], "grouped_partition_routers": [], "complex_dependencies": []}

        def find_performance_flags(config: Any, stream_name: str = None) -> None:
            if isinstance(config, dict):
                if config.get("incremental_dependency") is True:
                    if stream_name:
                        indicators["incremental_dependency_streams"].append(stream_name)

                if config.get("type") == "GroupingPartitionRouter":
                    underlying = config.get("underlying_partition_router", {})
                    if underlying.get("type") == "SubstreamPartitionRouter":
                        if stream_name:
                            indicators["grouped_partition_routers"].append(stream_name)

                if config.get("type") == "SubstreamPartitionRouter":
                    parent_configs = config.get("parent_stream_configs", [])
                    if len(parent_configs) > 1:
                        if stream_name:
                            indicators["complex_dependencies"].append(stream_name)

                for value in config.values():
                    find_performance_flags(value, stream_name)
            elif isinstance(config, list):
                for item in config:
                    find_performance_flags(item, stream_name)

        stream_definitions = manifest.get("definitions", {}).get("streams", {})
        for stream_name, stream_config in stream_definitions.items():
            find_performance_flags(stream_config, stream_name)

        return indicators

    def get_documented_interleaved_streams(self, metadata: Dict[str, Any]) -> List[List[str]]:
        """Extract documented interleaved streams from metadata.yaml."""
        data = metadata.get("data", {})
        interleaved_streams = data.get("interleavedStreams", {})
        return interleaved_streams.get("relationships", [])

    def generate_metadata_extension(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata.yaml extension for interleaved streams."""
        if not analysis["interleaved_streams"]:
            return {}

        extension = {"interleavedStreams": {"relationships": analysis["interleaved_streams"]}}

        if analysis["performance_indicators"]:
            hints = {}

            if analysis["performance_indicators"]["incremental_dependency_streams"]:
                hints["performanceCritical"] = analysis["performance_indicators"]["incremental_dependency_streams"]

            if analysis["performance_indicators"]["grouped_partition_routers"]:
                hints["optimizedGrouping"] = analysis["performance_indicators"]["grouped_partition_routers"]

            if analysis["performance_indicators"]["complex_dependencies"]:
                hints["complexDependencies"] = analysis["performance_indicators"]["complex_dependencies"]

            if hints:
                extension["interleavedStreams"]["optimizationHints"] = hints

        return extension

    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print a summary of detection results."""
        total_connectors = len(results)
        total_with_interleaved = sum(1 for r in results.values() if r["interleaved_streams"])
        total_undocumented = sum(1 for r in results.values() if r["needs_documentation"])
        total_with_performance = sum(1 for r in results.values() if r["has_performance_flags"])

        print(f"\n=== Interleaved Streams Detection Summary ===")
        print(f"Total connectors analyzed: {total_connectors}")
        print(f"Connectors with interleaved streams: {total_with_interleaved}")
        print(f"Connectors needing documentation: {total_undocumented}")
        print(f"Connectors with performance flags: {total_with_performance}")

        if total_undocumented > 0:
            print(f"\nConnectors needing documentation:")
            for name, analysis in results.items():
                if analysis["needs_documentation"]:
                    streams = analysis["interleaved_streams"]
                    print(f"  {name}: {streams}")


def main():
    parser = argparse.ArgumentParser(description="Detect interleaved streams in Airbyte connectors")
    parser.add_argument("connectors_path", help="Path to airbyte-integrations/connectors directory")
    parser.add_argument("--connector", help="Analyze specific connector only")
    parser.add_argument("--output", help="Output results to JSON file")
    parser.add_argument("--generate-metadata", action="store_true", help="Generate metadata.yaml extensions for undocumented streams")
    parser.add_argument("--summary-only", action="store_true", help="Show summary only")

    args = parser.parse_args()

    detector = InterleavedStreamDetector(args.connectors_path)

    if args.connector:
        connector_path = Path(args.connectors_path) / args.connector
        if not connector_path.exists():
            print(f"Connector {args.connector} not found", file=sys.stderr)
            sys.exit(1)

        results = {args.connector: detector.analyze_connector(connector_path)}
    else:
        results = detector.scan_all_connectors()

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")

    if not args.summary_only:
        for name, analysis in results.items():
            if analysis["interleaved_streams"]:
                print(f"\n{name}:")
                print(f"  Interleaved streams: {analysis['interleaved_streams']}")
                if analysis["performance_indicators"]["incremental_dependency_streams"]:
                    print(f"  Performance critical: {analysis['performance_indicators']['incremental_dependency_streams']}")
                if analysis["needs_documentation"]:
                    print(f"  ⚠️  Needs documentation in metadata.yaml")

    if args.generate_metadata:
        for name, analysis in results.items():
            if analysis["needs_documentation"]:
                extension = detector.generate_metadata_extension(analysis)
                output_path = f"{name}_metadata_extension.yaml"
                with open(output_path, "w") as f:
                    yaml.dump(extension, f, default_flow_style=False)
                print(f"Generated metadata extension: {output_path}")

    detector.print_summary(results)


if __name__ == "__main__":
    main()
