package io.airbyte.integrations.destination.snowflake.demo.file_based.api;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestination;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestinationFactory;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.RabbitMqDataWriter;

public class HttpStreamDestinationFactory implements StreamDestinationFactory<RabbitMqDataWriter.RabbitMqStorageLocation> {
  @Override
  public void setup(final JsonNode config) {

  }

  @Override
  public StreamDestination<RabbitMqDataWriter.RabbitMqStorageLocation> build(final StreamConfig stream) {
    return new HttpStreamDestination();
  }

  @Override
  public void close() throws Exception {

  }
}
