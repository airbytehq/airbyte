package io.airbyte.integrations.destination.snowflake.demo.file_based.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestination;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestinationFactory;

public class SnowflakeStreamDestinationFactory implements StreamDestinationFactory {

  @Override
  public void setup(final JsonNode config) {
    // open a connection pool, etc.
  }

  @Override
  public StreamDestination build(final StreamConfig stream) {
    // Pass the connection pool into this constructor
    return new SnowflakeStreamDestination(stream, null, null);
  }

  @Override
  public void close() throws Exception {
    // close the connection pool, etc.
  }
}
