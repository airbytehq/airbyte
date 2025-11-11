#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import copy
import hashlib
import json
from collections import defaultdict
from itertools import chain
from typing import Any, Callable, DefaultDict, Dict, Iterable, List, Optional, Tuple

from airbyte_cdk.sources.declarative.parsers.custom_exceptions import ManifestNormalizationException

# Type definitions for better readability
ManifestType = Dict[str, Any]
DefinitionsType = Dict[str, Any]
DuplicateOccurancesType = List[Tuple[List[str], Dict[str, Any], Dict[str, Any]]]
DuplicatesType = DefaultDict[str, DuplicateOccurancesType]

# Configuration constants
N_OCCURANCES = 2

DEF_TAG = "definitions"
LINKABLE_TAG = "linkable"
LINKED_TAG = "linked"
PROPERTIES_TAG = "properties"
SCHEMA_LOADER_TAG = "schema_loader"
SCHEMA_TAG = "schema"
SCHEMAS_TAG = "schemas"
STREAMS_TAG = "streams"


def _get_linkable_schema_tags(schema: DefinitionsType) -> List[str]:
    """
    Extracts linkable tags from schema definitions.
    This function identifies properties within a schema's definitions that are marked as linkable.
    It traverses through each definition in the schema, examines its properties, and collects
    the keys of properties that contain the LINKABLE_TAG.

    Args:
        schema (DefinitionsType): The schema definition dictionary to process

    Returns:
        List[str]: A deduplicated list of property keys that are marked as linkable
    """

    # the linkable scope: ['definitions.*']
    schema_definitions = schema.get(DEF_TAG, {})

    linkable_tags: List[str] = []
    # Extract linkable keys from properties

    extract_linkable_keys: Callable[[Dict[str, Dict[str, Any]]], List[str]] = lambda properties: [
        key for key, value in properties.items() if LINKABLE_TAG in value.keys()
    ]

    # Process each root value to get its linkable keys
    process_root: Callable[[Dict[str, Any]], List[str]] = lambda root_value: extract_linkable_keys(
        root_value.get(PROPERTIES_TAG, {})
    )

    # Map the process_root function over all schema values and flatten the results
    all_linkable_tags = chain.from_iterable(map(process_root, schema_definitions.values()))

    # Add all found linkable tags to the tags list
    linkable_tags.extend(all_linkable_tags)

    # return unique tags only
    return list(set(linkable_tags))


class ManifestNormalizer:
    """
    This class is responsible for normalizing the manifest by appliying processing such as:
     - removing duplicated definitions
     - replacing them with references.

    To extend the functionality, use the `normilize()` method to include any additional processing steps.
    """

    def __init__(
        self,
        resolved_manifest: ManifestType,
        declarative_schema: DefinitionsType,
    ) -> None:
        self._resolved_manifest = resolved_manifest
        self._declarative_schema = declarative_schema
        self._normalized_manifest: ManifestType = copy.deepcopy(self._resolved_manifest)
        # get the tags marked as `linkable` in the component schema
        self._linkable_tags = _get_linkable_schema_tags(self._declarative_schema)

    def to_json_str(self) -> str:
        return json.dumps(self._normalized_manifest, indent=2)

    def normalize(self) -> ManifestType:
        """
        Normalizes the manifest by deduplicating and resolving schema references.

        This method processes the manifest in two steps:
        1. Deduplicates elements within the manifest
        2. Resolves and references schemas

        Returns:
            ManifestType: The normalized manifest if processing succeeds,
                          or the original resolved manifest if normalization fails.

        Raises:
            ManifestNormalizationException: Caught internally and handled by returning the original manifest.
        """
        try:
            self._deduplicate_manifest()

            return self._normalized_manifest
        except ManifestNormalizationException:
            # if any error occurs, we just return the original manifest.
            # TODO: enable debug logging
            return self._resolved_manifest

    def _get_manifest_streams(self) -> Iterable[Dict[str, Any]]:
        """
        Get the streams from the manifest.

        Returns:
            An Iterable of streams.
        """

        if STREAMS_TAG in self._normalized_manifest.keys():
            for stream in self._normalized_manifest[STREAMS_TAG]:
                yield stream

        yield from []

    def _deduplicate_manifest(self) -> None:
        """
        Find commonalities in the input JSON structure and refactor it to avoid redundancy.
        """

        try:
            # prepare the `definitions` tag
            self._prepare_definitions()
            # replace duplicates with references, if any
            self._handle_duplicates(self._collect_duplicates())
            # replace parent streams with $refs
            self._replace_parent_streams_with_refs()
            # clean dangling fields after resolving $refs
            self._clean_dangling_fields()
        except Exception as e:
            raise ManifestNormalizationException(str(e))

    def _replace_parent_streams_with_refs(self) -> None:
        """
        For each stream in the manifest, if it has a retriever.partition_router with parent_stream_configs,
        replace any 'stream' fields in those configs that are dicts and deeply equal to another stream object
        with a $ref to the correct stream index.
        """
        streams = self._normalized_manifest.get(STREAMS_TAG, [])

        # Build a hash-to-index mapping for O(1) lookups
        stream_hash_to_index = {}
        for idx, stream in enumerate(streams):
            stream_hash = self._hash_object(stream)
            stream_hash_to_index[stream_hash] = idx

        for idx, stream in enumerate(streams):
            retriever = stream.get("retriever")
            if not retriever:
                continue
            partition_router = retriever.get("partition_router")
            routers = (
                partition_router
                if isinstance(partition_router, list)
                else [partition_router]
                if partition_router
                else []
            )
            for router in routers:
                if not isinstance(router, dict):
                    continue
                if router.get("type") != "SubstreamPartitionRouter":
                    continue
                parent_stream_configs = router.get("parent_stream_configs", [])
                for parent_config in parent_stream_configs:
                    if not isinstance(parent_config, dict):
                        continue
                    stream_ref = parent_config.get("stream")
                    # Only replace if it's a dict and matches any stream in the manifest
                    if stream_ref is not None and isinstance(stream_ref, dict):
                        stream_ref_hash = self._hash_object(stream_ref)
                        if stream_ref_hash in stream_hash_to_index:
                            parent_config["stream"] = {
                                "$ref": f"#/streams/{stream_hash_to_index[stream_ref_hash]}"
                            }

    def _clean_dangling_fields(self) -> None:
        """
        Clean the manifest by removing unused definitions and schemas.
        This method removes any definitions or schemas that are not referenced by any $ref in the manifest.
        """

        def find_all_refs(obj: Dict[str, Any], refs: List[str]) -> None:
            """
            Recursively find all $ref paths in the object.

            Args:
                obj: The object to search through
                refs: List to store found reference paths
            """
            if not isinstance(obj, dict):
                return

            for key, value in obj.items():
                if key == "$ref" and isinstance(value, str):
                    # Remove the leading #/ from the ref path
                    refs.append(value[2:])
                elif isinstance(value, dict):
                    find_all_refs(value, refs)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            find_all_refs(item, refs)

        def clean_section(section: Dict[str, Any], section_path: str) -> None:
            """
            Clean a section by removing unreferenced fields.

            Args:
                section: The section to clean
                section_path: The path to this section in the manifest
            """
            for key in list(section.keys()):
                current_path = f"{section_path}/{key}"
                # Check if this path is referenced or is a parent of a referenced path
                if not any(ref.startswith(current_path) for ref in all_refs):
                    del section[key]

        # Find all references in the manifest
        all_refs: List[str] = []
        find_all_refs(self._normalized_manifest, all_refs)

        # Clean definitions
        if DEF_TAG in self._normalized_manifest:
            clean_section(self._normalized_manifest[DEF_TAG], DEF_TAG)
            # Remove empty definitions section
            if not self._normalized_manifest[DEF_TAG]:
                del self._normalized_manifest[DEF_TAG]

        # Clean schemas
        if SCHEMAS_TAG in self._normalized_manifest:
            clean_section(self._normalized_manifest[SCHEMAS_TAG], SCHEMAS_TAG)
            # Remove empty schemas section
            if not self._normalized_manifest[SCHEMAS_TAG]:
                del self._normalized_manifest[SCHEMAS_TAG]

    def _prepare_definitions(self) -> None:
        """
        Clean the definitions in the manifest by removing unnecessary properties.
        This function modifies the manifest in place.
        """

        # Check if the definitions tag exists
        if not DEF_TAG in self._normalized_manifest:
            self._normalized_manifest[DEF_TAG] = {}

        # Check if the linked tag exists
        if not LINKED_TAG in self._normalized_manifest[DEF_TAG]:
            self._normalized_manifest[DEF_TAG][LINKED_TAG] = {}

        # remove everything from definitions tag except of `linked`, after processing
        for key in list(self._normalized_manifest[DEF_TAG].keys()):
            if key != LINKED_TAG:
                self._normalized_manifest[DEF_TAG].pop(key, None)

    def _replace_duplicates_with_refs(self, duplicates: DuplicatesType) -> None:
        """
        Process duplicate objects and replace them with references.

        Args:
            duplicates: The duplicates dictionary collected from the given manifest.
        """

        for _, occurrences in duplicates.items():
            type_key, key, value = self._get_occurance_samples(occurrences)
            is_linked_def = self._is_linked_definition(type_key, key)

            # Add to definitions if not there already
            if not is_linked_def:
                self._add_to_linked_definitions(type_key, key, value)

            # Replace occurrences with references
            for _, parent_obj, value in occurrences:
                if is_linked_def:
                    if value == self._get_linked_definition_value(type_key, key):
                        parent_obj[key] = self._create_linked_definition_ref(type_key, key)
                else:
                    parent_obj[key] = self._create_linked_definition_ref(type_key, key)

    def _handle_duplicates(self, duplicates: DuplicatesType) -> None:
        """
        Process the duplicates and replace them with references.

        Args:
            duplicates: The duplicates dictionary collected from the given manifest.
        """

        if len(duplicates) > 0:
            self._replace_duplicates_with_refs(duplicates)

    def _add_duplicate(
        self,
        duplicates: DuplicatesType,
        current_path: List[str],
        obj: Dict[str, Any],
        value: Any,
        key: Optional[str] = None,
    ) -> None:
        """
        Adds a duplicate record of an observed object by computing a unique hash for the provided value.

        This function computes a hash for the given value (or a dictionary composed of the key and value if a key is provided)
        and appends a tuple containing the current path, the original object, and the value to the duplicates
        dictionary under the corresponding hash.

        Parameters:
            duplicates (DuplicatesType): The dictionary to store duplicate records.
            current_path (List[str]): The list of keys or indices representing the current location in the object hierarchy.
            obj (Dict): The original dictionary object where the duplicate is observed.
            value (Any): The value to be hashed and used for identifying duplicates.
            key (Optional[str]): An optional key that, if provided, wraps the value in a dictionary before hashing.
        """

        # create hash for each duplicate observed
        value_to_hash = {key: value} if key is not None else value
        duplicates[self._hash_object(value_to_hash)].append((current_path, obj, value))

    def _add_to_linked_definitions(
        self,
        type_key: str,
        key: str,
        value: Any,
    ) -> None:
        """
        Add a value to the linked definitions under the specified key.

        Args:
            definitions: The definitions dictionary to modify
            key: The key to use
            value: The value to add
        """
        if type_key not in self._normalized_manifest[DEF_TAG][LINKED_TAG].keys():
            self._normalized_manifest[DEF_TAG][LINKED_TAG][type_key] = {}

        if key not in self._normalized_manifest[DEF_TAG][LINKED_TAG][type_key].keys():
            self._normalized_manifest[DEF_TAG][LINKED_TAG][type_key][key] = value

    def _collect_duplicates(self) -> DuplicatesType:
        """
        Traverse the JSON object and collect all potential duplicate values and objects.

        Returns:
            duplicates: A dictionary of duplicate objects.
        """

        def _collect(obj: Dict[str, Any], path: Optional[List[str]] = None) -> None:
            """
            The closure to recursively collect duplicates in the JSON object.

            Args:
                obj: The current object being analyzed.
                path: The current path in the object hierarchy.
            """

            if not isinstance(obj, dict):
                return

            path = [] if path is None else path
            # Check if the object is empty
            for key, value in obj.items():
                # do not collect duplicates from `definitions` tag
                if key == DEF_TAG:
                    continue

                current_path = path + [key]

                if isinstance(value, dict):
                    # First process nested dictionaries
                    _collect(value, current_path)
                    # Process allowed-only component tags
                    if key in self._linkable_tags:
                        self._add_duplicate(duplicates, current_path, obj, value)

                # handle primitive types
                elif isinstance(value, (str, int, float, bool)):
                    # Process allowed-only field tags
                    if key in self._linkable_tags:
                        self._add_duplicate(duplicates, current_path, obj, value, key)

                # handle list cases
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        _collect(item, current_path + [str(i)])

        duplicates: DuplicatesType = defaultdict(list, {})
        try:
            if self._linkable_tags:
                _collect(self._normalized_manifest)
                # clean non-duplicates and sort based on the count of occurrences
                return self._clean_and_sort_duplicates(duplicates)
            return duplicates
        except Exception as e:
            raise ManifestNormalizationException(str(e))

    def _clean_and_sort_duplicates(self, duplicates: DuplicatesType) -> DuplicatesType:
        """
        Clean non-duplicates and sort the duplicates by their occurrences.

        Args:
            duplicates: The duplicates dictionary to sort

        Returns:
            A sorted duplicates dictionary.
        """

        # clean non-duplicates
        duplicates = defaultdict(
            list,
            {k: v for k, v in duplicates.items() if len(v) >= N_OCCURANCES},
        )

        # sort the duplicates by their occurrences, more frequent ones go first
        duplicates = defaultdict(
            list,
            {k: v for k, v in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)},
        )

        return duplicates

    def _hash_object(self, obj: Dict[str, Any]) -> str:
        """
        Create a unique hash for a dictionary object.

        Args:
            node: The dictionary to hash

        Returns:
            A hashed string
        """

        # Sort keys to ensure consistent hash for same content
        return hashlib.md5(json.dumps(obj, sort_keys=True).encode()).hexdigest()

    def _is_linked_definition(self, type_key: str, key: str) -> bool:
        """
        Check if the key already exists in the linked definitions.

        Args:
            key: The key to check
            definitions: The definitions dictionary with definitions

        Returns:
            True if the key exists in the linked definitions, False otherwise
        """

        if type_key in self._normalized_manifest[DEF_TAG][LINKED_TAG].keys():
            # Check if the key exists in the linked definitions
            if key in self._normalized_manifest[DEF_TAG][LINKED_TAG][type_key].keys():
                return True

        return False

    def _get_linked_definition_value(self, type_key: str, key: str) -> Any:
        """
        Get the value of a linked definition by its key.

        Args:
            key: The key to check
            definitions: The definitions dictionary with definitions

        Returns:
            The value of the linked definition
        """
        if type_key in self._normalized_manifest[DEF_TAG][LINKED_TAG].keys():
            if key in self._normalized_manifest[DEF_TAG][LINKED_TAG][type_key].keys():
                return self._normalized_manifest[DEF_TAG][LINKED_TAG][type_key][key]
        else:
            raise ManifestNormalizationException(
                f"Key {key} not found in linked definitions. Please check the manifest."
            )

    def _get_occurance_samples(self, occurrences: DuplicateOccurancesType) -> Tuple[str, str, Any]:
        """
        Get the key from the occurrences list.

        Args:
            occurrences: The occurrences list

        Returns:
            The key, type and value from the occurrences
        """

        # Take the value from the first occurrence, as they are the same
        path, obj, value = occurrences[0]
        return (
            obj["type"],
            path[-1],
            value,
        )  # Return the component's name as the last part of its path

    def _create_linked_definition_ref(self, type_key: str, key: str) -> Dict[str, str]:
        """
        Create a reference object for the linked definitions using the specified key.

        Args:
            ref_key: The reference key to use

        Returns:
            A reference object in the proper format
        """

        return {"$ref": f"#/{DEF_TAG}/{LINKED_TAG}/{type_key}/{key}"}
