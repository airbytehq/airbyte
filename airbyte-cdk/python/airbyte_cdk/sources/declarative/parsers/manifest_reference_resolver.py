#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from typing import Any, Mapping, Set, Tuple, Union

from airbyte_cdk.sources.declarative.parsers.custom_exceptions import CircularReferenceException, UndefinedReferenceException

REF_TAG = "$ref"


class ManifestReferenceResolver:
    """
    An incoming manifest can contain references to values previously defined.
    This parser will dereference these values to produce a complete ConnectionDefinition.

    References can be defined using a #/<arg> string.
    ```
    key: 1234
    reference: "#/key"
    ```
    will produce the following definition:
    ```
    key: 1234
    reference: 1234
    ```
    This also works with objects:
    ```
    key_value_pairs:
      k1: v1
      k2: v2
    same_key_value_pairs: "#/key_value_pairs"
    ```
    will produce the following definition:
    ```
    key_value_pairs:
      k1: v1
      k2: v2
    same_key_value_pairs:
      k1: v1
      k2: v2
    ```

    The $ref keyword can be used to refer to an object and enhance it with addition key-value pairs
    ```
    key_value_pairs:
      k1: v1
      k2: v2
    same_key_value_pairs:
      $ref: "#/key_value_pairs"
      k3: v3
    ```
    will produce the following definition:
    ```
    key_value_pairs:
      k1: v1
      k2: v2
    same_key_value_pairs:
      k1: v1
      k2: v2
      k3: v3
    ```

    References can also point to nested values.
    Nested references are ambiguous because one could define a key containing with `.`
    in this example, we want to refer to the limit key in the dict object:
    ```
    dict:
        limit: 50
    limit_ref: "#/dict/limit"
    ```
    will produce the following definition:
    ```
    dict
        limit: 50
    limit-ref: 50
    ```

    whereas here we want to access the `nested/path` value.
    ```
    nested:
        path: "first one"
    nested/path: "uh oh"
    value: "#/nested/path
    ```
    will produce the following definition:
    ```
    nested:
        path: "first one"
    nested/path: "uh oh"
    value: "uh oh"
    ```

    to resolve the ambiguity, we try looking for the reference key at the top level, and then traverse the structs downward
    until we find a key with the given path, or until there is nothing to traverse.
    """

    def preprocess_manifest(self, manifest: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        :param manifest: incoming manifest that could have references to previously defined components
        :return:
        """
        return self._evaluate_node(manifest, manifest, set())

    def _evaluate_node(self, node: Any, manifest: Mapping[str, Any], visited: Set) -> Any:
        if isinstance(node, dict):
            evaluated_dict = {k: self._evaluate_node(v, manifest, visited) for k, v in node.items() if not self._is_ref_key(k)}
            if REF_TAG in node:
                # The node includes a $ref key, so we splat the referenced value(s) into the evaluated dict
                evaluated_ref = self._evaluate_node(node[REF_TAG], manifest, visited)
                if not isinstance(evaluated_ref, dict):
                    return evaluated_ref
                else:
                    # The values defined on the component take precedence over the reference values
                    return evaluated_ref | evaluated_dict
            else:
                return evaluated_dict
        elif isinstance(node, list):
            return [self._evaluate_node(v, manifest, visited) for v in node]
        elif self._is_ref(node):
            if node in visited:
                raise CircularReferenceException(node)
            visited.add(node)
            ret = self._evaluate_node(self._lookup_ref_value(node, manifest), manifest, visited)
            visited.remove(node)
            return ret
        else:
            return node

    def _lookup_ref_value(self, ref: str, manifest: Mapping[str, Any]) -> Any:
        path = re.match(r"#/(.*)", ref).groups()[0]
        if not path:
            raise UndefinedReferenceException(path, ref)
        try:
            return self._read_ref_value(path, manifest)
        except (AttributeError, KeyError, IndexError):
            raise UndefinedReferenceException(path, ref)

    @staticmethod
    def _is_ref(node: Any) -> bool:
        return isinstance(node, str) and node.startswith("#/")

    @staticmethod
    def _is_ref_key(key) -> bool:
        return key == REF_TAG

    @staticmethod
    def _read_ref_value(ref: str, manifest_node: Mapping[str, Any]) -> Any:
        """
        Read the value at the referenced location of the manifest.

        References are ambiguous because one could define a key containing `/`
        In this example, we want to refer to the `limit` key in the `dict` object:
            dict:
                limit: 50
            limit_ref: "#/dict/limit"

        Whereas here we want to access the `nested/path` value.
          nested:
            path: "first one"
          nested/path: "uh oh"
          value: "#/nested/path"

        To resolve the ambiguity, we try looking for the reference key at the top level, and then traverse the structs downward
        until we find a key with the given path, or until there is nothing to traverse.

        Consider the path foo/bar/baz. To resolve the ambiguity, we first try 'foo/bar/baz' in its entirety as a top-level key. If this
        fails, we try 'foo' as the top-level key, and if this succeeds, pass 'bar/baz' on as the key to be tried at the next level.
        """
        while ref:
            try:
                return manifest_node[ref]
            except (KeyError, TypeError):
                head, ref = _parse_path(ref)
                manifest_node = manifest_node[head]
        return manifest_node


def _parse_path(ref: str) -> Tuple[Union[str, int], str]:
    """
    Return the next path component, together with the rest of the path.

    A path component may be a string key, or an int index.

    >>> _parse_path("foo/bar")
    "foo", "bar"
    >>> _parse_path("foo/7/8/bar")
    "foo", "7/8/bar"
    >>> _parse_path("7/8/bar")
    7, "8/bar"
    >>> _parse_path("8/bar")
    8, "bar"
    >>> _parse_path("8foo/bar")
    "8foo", "bar"
    """
    match = re.match(r"([^/]*)/?(.*)", ref)
    first, rest = match.groups()
    try:
        return int(first), rest
    except ValueError:
        return first, rest
