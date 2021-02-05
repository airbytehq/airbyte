package io.airbyte.activities;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteCatalog;

import java.io.IOException;

public interface DiscoverCatalogActivity {
    AirbyteCatalog discoverCatalog(String dockerImage, JsonNode connectionConfig) throws IOException;
}
