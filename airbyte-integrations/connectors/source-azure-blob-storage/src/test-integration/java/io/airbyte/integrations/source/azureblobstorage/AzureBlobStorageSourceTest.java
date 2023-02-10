package io.airbyte.integrations.source.azureblobstorage;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AzureBlobStorageSourceTest {

    private AzureBlobStorageSource azureBlobStorageSource;

    @BeforeEach
    void setup() {
        azureBlobStorageSource = new AzureBlobStorageSource();
    }

    @Test
    void test() throws Exception {

        azureBlobStorageSource.check(null);

    }

}
