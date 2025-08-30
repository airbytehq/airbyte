# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Test for detecting undeclared interleaved streams in connectors."""
import pytest
import yaml
from pathlib import Path
from typing import Dict, Any, List, Set

from connector_acceptance_test.base import BaseTest
from connector_acceptance_test.config import Config


class TestInterleavedStreams(BaseTest):
    """Test that interleaved streams are properly declared in metadata.yaml."""
    
    def test_interleaved_streams_declared(self, connector_config: Config):
        """Test that connectors with SubstreamPartitionRouter patterns declare interleaved streams."""
        manifest_path = Path(connector_config.connector_dir) / "manifest.yaml"
        metadata_path = Path(connector_config.connector_dir) / "metadata.yaml"
        
        if not manifest_path.exists():
            pytest.skip("No manifest.yaml found - not a low-code connector")
        
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = yaml.safe_load(f)
        
        detected_streams = self._detect_interleaved_streams(manifest)
        
        if not detected_streams:
            pytest.skip("No interleaved streams detected")
        
        documented_streams = self._get_documented_interleaved_streams(metadata)
        
        if not documented_streams:
            pytest.fail(
                f"Connector has interleaved streams {detected_streams} but they are not "
                f"declared in metadata.yaml. Please add an 'interleavedStreams' section "
                f"to your metadata.yaml file."
            )
        
        self._validate_documented_streams(detected_streams, documented_streams)
    
    def _detect_interleaved_streams(self, manifest: Dict[str, Any]) -> List[List[str]]:
        """Detect SubstreamPartitionRouter patterns in manifest."""
        interleaved_groups = []
        stream_definitions = manifest.get('definitions', {}).get('streams', {})
        
        relationships = {}  # child -> [parents]
        
        for stream_name, stream_config in stream_definitions.items():
            parents = self._extract_parent_streams(stream_config)
            if parents:
                relationships[stream_name] = parents
        
        processed = set()
        
        for child_stream, parent_streams in relationships.items():
            if child_stream in processed:
                continue
                
            group = self._build_dependency_chain(child_stream, relationships)
            if len(group) > 1:  # Only include groups with actual dependencies
                interleaved_groups.append(sorted(group))
                processed.update(group)
        
        return interleaved_groups
    
    def _extract_parent_streams(self, stream_config: Dict[str, Any]) -> List[str]:
        """Extract parent stream names from a stream configuration."""
        parents = []
        
        def find_substream_routers(config: Any) -> None:
            if isinstance(config, dict):
                if config.get('type') == 'SubstreamPartitionRouter':
                    parent_configs = config.get('parent_stream_configs', [])
                    for parent_config in parent_configs:
                        stream_ref = parent_config.get('stream', '')
                        if isinstance(stream_ref, str) and stream_ref.startswith('#/definitions/streams/'):
                            parent_name = stream_ref.split('/')[-1]
                            parents.append(parent_name)
                        elif isinstance(stream_ref, dict) and '$ref' in stream_ref:
                            ref = stream_ref['$ref']
                            if ref.startswith('#/definitions/streams/'):
                                parent_name = ref.split('/')[-1]
                                parents.append(parent_name)
                
                for value in config.values():
                    find_substream_routers(value)
            elif isinstance(config, list):
                for item in config:
                    find_substream_routers(item)
        
        find_substream_routers(stream_config)
        return list(set(parents))  # Remove duplicates
    
    def _build_dependency_chain(self, start_stream: str, relationships: Dict[str, List[str]], visited: Set[str] = None) -> set:
        """Build a complete dependency chain starting from a stream."""
        if visited is None:
            visited = set()
        
        if start_stream in visited:
            return {start_stream}  # Avoid infinite recursion
        
        visited.add(start_stream)
        chain = {start_stream}
        
        if start_stream in relationships:
            for parent in relationships[start_stream]:
                chain.update(self._build_dependency_chain(parent, relationships, visited.copy()))
        
        for child, parents in relationships.items():
            if start_stream in parents:
                chain.update(self._build_dependency_chain(child, relationships, visited.copy()))
        
        return chain
    
    def _get_documented_interleaved_streams(self, metadata: Dict[str, Any]) -> List[List[str]]:
        """Extract documented interleaved streams from metadata.yaml."""
        data = metadata.get('data', {})
        interleaved_streams = data.get('interleavedStreams', {})
        return interleaved_streams.get('relationships', [])
    
    def _validate_documented_streams(self, detected: List[List[str]], documented: List[List[str]]) -> None:
        """Validate that documented streams cover detected patterns."""
        detected_sets = [set(group) for group in detected]
        documented_sets = [set(group) for group in documented]
        
        for detected_group in detected_sets:
            covered = False
            for documented_group in documented_sets:
                if detected_group.issubset(documented_group) or len(detected_group.intersection(documented_group)) >= len(detected_group) * 0.8:
                    covered = True
                    break
            
            if not covered:
                pytest.fail(
                    f"Detected interleaved stream group {sorted(detected_group)} is not "
                    f"properly documented in metadata.yaml. Current documentation: {documented}"
                )
    
    def test_performance_flags_consistency(self, connector_config: Config):
        """Test that performance flags are consistent with interleaved stream declarations."""
        manifest_path = Path(connector_config.connector_dir) / "manifest.yaml"
        metadata_path = Path(connector_config.connector_dir) / "metadata.yaml"
        
        if not manifest_path.exists() or not metadata_path.exists():
            pytest.skip("Missing manifest.yaml or metadata.yaml")
        
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        with open(metadata_path, 'r') as f:
            metadata = yaml.safe_load(f)
        
        performance_streams = self._detect_performance_flags(manifest)
        documented_streams = self._get_documented_interleaved_streams(metadata)
        
        if performance_streams and documented_streams:
            data = metadata.get('data', {})
            interleaved_streams = data.get('interleavedStreams', {})
            optimization_hints = interleaved_streams.get('optimizationHints', {})
            
            performance_critical = optimization_hints.get('performanceCritical', [])
            
            for stream in performance_streams:
                stream_group = None
                for group in documented_streams:
                    if stream in group:
                        stream_group = group
                        break
                
                if stream_group and stream not in performance_critical:
                    pytest.fail(
                        f"Stream '{stream}' has incremental_dependency=true but is not "
                        f"marked as performanceCritical in metadata.yaml optimization hints"
                    )
    
    def _detect_performance_flags(self, manifest: Dict[str, Any]) -> List[str]:
        """Detect streams with performance flags like incremental_dependency=true."""
        performance_streams = []
        
        def find_performance_flags(config: Any, stream_name: str = None) -> None:
            if isinstance(config, dict):
                if config.get('incremental_dependency') is True and stream_name:
                    performance_streams.append(stream_name)
                
                for value in config.values():
                    find_performance_flags(value, stream_name)
            elif isinstance(config, list):
                for item in config:
                    find_performance_flags(item, stream_name)
        
        stream_definitions = manifest.get('definitions', {}).get('streams', {})
        for stream_name, stream_config in stream_definitions.items():
            find_performance_flags(stream_config, stream_name)
        
        return performance_streams
