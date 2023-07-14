/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.Map;

public class AzureBlobStorageDataFactory {

  private AzureBlobStorageDataFactory() {

  }

  static JsonNode createAzureBlobStorageConfig(String host, String container) {
    return Jsons.jsonNode(Map.of(
        "azure_blob_storage_endpoint", host + "/devstoreaccount1",
        "azure_blob_storage_account_name", "devstoreaccount1",
        "azure_blob_storage_account_key",
        "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
        "azure_blob_storage_container_name", container,
        "azure_blob_storage_blobs_prefix", "FolderA/FolderB/",
        "azure_blob_storage_schema_inference_limit", 10L,
        "format", Jsons.deserialize("""
                                    {
                                      "format_type": "JSONL"
                                    }""")));
  }

  static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog(String streamName) {
    return new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of(AzureBlobAdditionalProperties.LAST_MODIFIED))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                streamName,
                Field.of("attr_1", JsonSchemaType.STRING),
                Field.of("attr_2", JsonSchemaType.INTEGER),
                Field.of(AzureBlobAdditionalProperties.LAST_MODIFIED, JsonSchemaType.TIMESTAMP_WITH_TIMEZONE_V1),
                Field.of(AzureBlobAdditionalProperties.BLOB_NAME, JsonSchemaType.STRING))
                .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

}
