package io.airbyte.integrations.destination.snowflake.demo.file_based.iface;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;

public interface StreamDestinationFactory extends AutoCloseable {
  void setup(JsonNode config);
  StreamDestination build(StreamConfig stream);
}
