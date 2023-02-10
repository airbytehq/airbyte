package io.airbyte.integrations.source.azureblobstorage;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AzureBlobStorageOperationsTest {

    private AzureBlobStorageContainer azureBlobStorageContainer;

    private AzureBlobStorageOperations azureBlobStorageOperations;

    @BeforeEach
    void setup() {
        azureBlobStorageContainer = new AzureBlobStorageContainer().withExposedPorts(10000);
        azureBlobStorageContainer.start();
        var azureBlobStorageConfig = new AzureBlobStorageConfig(
            "http://127.0.0.1:" + azureBlobStorageContainer.getMappedPort(10000) + "/devstoreaccount1",
            "devstoreaccount1",
            "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
            "airbyte-container",
            "FolderA/FolderB/",
            "",
            "",
            new AzureBlobStorageConfig.FormatConfig(AzureBlobStorageConfig.FormatConfig.Format.JSON)
        );
        azureBlobStorageOperations = new AzureBlobStorageOperations(azureBlobStorageConfig);
    }

    @AfterEach
    void tearDown() {
        azureBlobStorageContainer.stop();
        azureBlobStorageContainer.close();
    }

    @Test
    void test() {

    }

}
