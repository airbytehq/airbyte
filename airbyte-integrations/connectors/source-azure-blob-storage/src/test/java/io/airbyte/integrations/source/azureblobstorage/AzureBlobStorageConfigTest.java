/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.commons.json.Jsons;
import java.util.Map;
import org.junit.jupiter.api.Test;

class AzureBlobStorageConfigTest {

  @Test
  void testAzureBlobStorageConfig() {
    var jsonConfig = Jsons.jsonNode(Map.of(
        "azure_blob_storage_endpoint", "http://127.0.0.1:10000/devstoreaccount1",
        "azure_blob_storage_account_name", "devstoreaccount1",
        "azure_blob_storage_account_key",
        "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
        "azure_blob_storage_container_name", "airbyte-container",
        "azure_blob_storage_blobs_prefix", "FolderA/FolderB/",
        "azure_blob_storage_schema_inference_limit", 10L,
        "format", Jsons.deserialize("""
                                    {
                                      "format_type": "JSONL"
                                    }""")));

    var azureBlobStorageConfig = AzureBlobStorageConfig.createAzureBlobStorageConfig(jsonConfig);

    assertThat(azureBlobStorageConfig)
        .hasFieldOrPropertyWithValue("endpoint", "http://127.0.0.1:10000/devstoreaccount1")
        .hasFieldOrPropertyWithValue("accountName", "devstoreaccount1")
        .hasFieldOrPropertyWithValue("accountKey",
            "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==")
        .hasFieldOrPropertyWithValue("containerName", "airbyte-container")
        .hasFieldOrPropertyWithValue("prefix", "FolderA/FolderB/")
        .hasFieldOrPropertyWithValue("schemaInferenceLimit", 10L)
        .hasFieldOrPropertyWithValue("formatConfig", new AzureBlobStorageConfig.FormatConfig(
            AzureBlobStorageConfig.FormatConfig.Format.JSONL));

  }

}
