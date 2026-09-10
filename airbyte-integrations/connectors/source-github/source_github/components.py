#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Custom low-code components for source-github.

Everything here exists because the GitHub GraphQL responses cannot be reshaped into the
connector's long-standing REST-compatible record shape with declarative transformations
alone. Pagination, page-size reduction, error handling and incremental behavior are all
handled by the manifest.
"""

import base64
import binascii
import logging
import struct
from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


LOGGER = logging.getLogger("airbyte")

# GitHub's GraphQL reaction content enum, mapped to the field names the REST API used and
# therefore to the names already present in the `releases` schema and in user warehouses.
GRAPHQL_REACTION_TO_REST = {
    "THUMBS_UP": "plus_one",
    "THUMBS_DOWN": "minus_one",
    "LAUGH": "laugh",
    "HOORAY": "hooray",
    "CONFUSED": "confused",
    "HEART": "heart",
    "ROCKET": "rocket",
    "EYES": "eyes",
}


def _extract_database_id_from_node_id(node_id: Optional[str]) -> Optional[int]:
    """Extract the numeric database ID from a GitHub GraphQL Node ID.

    GitHub Node IDs with type prefixes (e.g. 'RA_...') are URL-safe base64 encodings of a
    msgpack array: [type_flag, repo_database_id, entity_database_id]. The last 4 bytes encode
    the entity's numeric database ID as a big-endian uint32.

    Release assets are the only place this is needed: the GraphQL `ReleaseAsset` type exposes
    no `databaseId`, but the REST-shaped schema has always carried a numeric `id`.
    """
    if not node_id or "_" not in node_id:
        return None
    try:
        encoded = node_id.split("_", 1)[1]
        decoded = base64.urlsafe_b64decode(encoded + "==")
        if len(decoded) >= 4:
            return struct.unpack(">I", decoded[-4:])[0]
    except (ValueError, struct.error, binascii.Error):
        return None
    return None


@dataclass
class ReleasesRecordTransformation(RecordTransformation):
    """Reshape a GraphQL `Release` node into the REST-compatible `releases` record.

    Ported verbatim from the legacy `streams.Releases.parse_response`. Five separate
    concerns, none of them expressible as AddFields/RemoveFields:

    - `assets`: unwrap the connection, flatten `uploader` to `uploader_id`, and recover each
      asset's numeric `id` from its node ID.
    - `reactions`: collapse `reactionGroups` into the REST reaction-count object, including
      the zero entries for reactions nobody used and the `total_count` sum.
    - `mentions_count`: unwrap a `totalCount`-only connection.
    - `target_commitish`: unwrap `tagCommit.oid`.
    - `url`/`assets_url`/`upload_url`/`tarball_url`/`zipball_url`: GraphQL does not return
      these, so they are synthesized from the repository, release ID and tag, exactly as the
      REST payload had them.
    """

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        repository = (stream_slice or {}).get("repository")
        record["repository"] = repository

        if record.get("author"):
            record["author"]["type"] = record["author"].pop("__typename", "User")

        record["assets"] = self._assets(record)
        record["reactions"] = self._reactions(record)

        mentions_connection = record.pop("mentions_connection", None)
        if mentions_connection is not None:
            record["mentions_count"] = mentions_connection.get("totalCount", 0)

        tag_commit = record.pop("tagCommit", None)
        record["target_commitish"] = tag_commit.get("target_commitish") if tag_commit else None

        api_url = (config or {}).get("api_url") or "https://api.github.com"
        record.update(
            self._rest_urls(
                api_url=api_url.rstrip("/"),
                repository=repository,
                release_id=record.get("id"),
                tag_name=record.get("tag_name"),
            )
        )

    def _assets(self, record: Mapping[str, Any]) -> list:
        assets_data = record.get("assets") or {}
        if (assets_data.get("pageInfo") or {}).get("hasNextPage"):
            # The query asks for `releaseAssets(first: 100)` and the manifest paginates the
            # releases connection only, so a release with more than 100 assets is truncated.
            # Warn rather than fail, which is what the Python stream did.
            LOGGER.warning(
                "Release %s in %s has >100 assets; only the first 100 were synced. "
                "Sub-pagination for release assets is not yet implemented.",
                record.get("id"),
                record.get("repository"),
            )
        assets = assets_data.get("nodes", [])
        for asset in assets:
            uploader = asset.pop("uploader", None)
            asset["uploader_id"] = uploader.get("id") if uploader else None
            asset["id"] = _extract_database_id_from_node_id(asset.get("node_id"))
        return assets

    def _reactions(self, record: MutableMapping[str, Any]) -> Optional[Mapping[str, Any]]:
        reaction_groups = record.pop("reaction_groups", None)
        if reaction_groups is None:
            return None
        reactions: MutableMapping[str, Any] = {key: 0 for key in GRAPHQL_REACTION_TO_REST.values()}
        total = 0
        for group in reaction_groups:
            rest_key = GRAPHQL_REACTION_TO_REST.get(group.get("content"))
            if rest_key:
                count = (group.get("reactors") or {}).get("totalCount", 0)
                reactions[rest_key] = count
                total += count
        reactions["total_count"] = total
        return reactions

    @staticmethod
    def _rest_urls(api_url: str, repository: Optional[str], release_id: Optional[int], tag_name: Optional[str]) -> Mapping[str, Any]:
        upload_url = api_url.replace("api.github.com", "uploads.github.com")
        return {
            "url": f"{api_url}/repos/{repository}/releases/{release_id}",
            "assets_url": f"{api_url}/repos/{repository}/releases/{release_id}/assets",
            "upload_url": f"{upload_url}/repos/{repository}/releases/{release_id}/assets{{?name,label}}",
            "tarball_url": f"{api_url}/repos/{repository}/tarball/{tag_name}" if tag_name else None,
            "zipball_url": f"{api_url}/repos/{repository}/zipball/{tag_name}" if tag_name else None,
        }
