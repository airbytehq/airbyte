package io.airbyte.integrations.destination.snowflake.demo.file_based.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestination;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestinationFactory;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.LocalFileDataWriter;

public class SnowflakeStreamDestinationFactory implements StreamDestinationFactory<LocalFileDataWriter.LocalFileLocation> {

  @Override
  public void setup(final JsonNode config) {
    // open a connection pool, etc.
  }

  @Override
  public StreamDestination<LocalFileDataWriter.LocalFileLocation> build(final StreamConfig stream) {
    // Pass the connection pool into this constructor
    return new SnowflakeStreamDestination(stream, null, null);
  }

  @Override
  public void close() throws Exception {
    // close the connection pool, etc.
  }
}
