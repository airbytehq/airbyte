package io.airbyte.integrations.source.azureblobstorage;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.commons.json.Jsons;
import java.util.Map;
import org.junit.jupiter.api.Test;

class AzureBlobStorageConfigTest {

    @Test
    void testAzureBlobStorageConfig() {

        //TODO (itaseski) add format config in config
        var jsonConfig = Jsons.jsonNode(Map.of(
            "azure_blob_storage_endpoint", "http://127.0.0.1:10000/devstoreaccount1",
            "azure_blob_storage_account_name", "devstoreaccount1",
            "azure_blob_storage_account_key",
            "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
            "azure_blob_storage_container_name", "airbyte-container",
            "azure_blob_storage_blobs_prefix", "FolderA/FolderB/",
            "azure_blob_storage_blobs_tags", "\"Rank\" >= '010' AND \"Rank\" < '100'",
            "azure_blob_storage_blobs_schema", "{}"));

        var azureBlobStorageConfig = AzureBlobStorageConfig.createAzureBlobStorageConfig(jsonConfig);

        assertThat(azureBlobStorageConfig)
            .hasFieldOrPropertyWithValue("endpoint", "http://127.0.0.1:10000/devstoreaccount1")
            .hasFieldOrPropertyWithValue("accountName", "devstoreaccount1")
            .hasFieldOrPropertyWithValue("accountKey",
                "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==")
            .hasFieldOrPropertyWithValue("containerName", "airbyte-container")
            .hasFieldOrPropertyWithValue("prefix", "FolderA/FolderB/")
            .hasFieldOrPropertyWithValue("blobsTags", "\"Rank\" >= '010' AND \"Rank\" < '100'")
            .hasFieldOrPropertyWithValue("schema", "{}");

    }

}
