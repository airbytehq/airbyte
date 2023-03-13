package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;

@FunctionalInterface
public interface Check {

  AirbyteConnectionStatus check(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception;

}
