package io.airbyte.integrations.destination.snowflake.demo.file_based.iface;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.StorageLocation;

public interface StreamDestinationFactory<T extends StorageLocation> extends AutoCloseable {
  void setup(JsonNode config);
  StreamDestination<T> build(StreamConfig stream);
}
