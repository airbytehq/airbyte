package io.airbyte.integrations.destination.snowflake.demo.file_based.api;

import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestination;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.RabbitMqDataWriter;

public class HttpStreamDestination implements StreamDestination<RabbitMqDataWriter.RabbitMqStorageLocation> {
  private final String endpoint;

  @Override
  public void setup() throws Exception {

  }

  @Override
  public void upload(final RabbitMqDataWriter.RabbitMqStorageLocation location, final int numRecords, final int numBytes) throws Exception {
    // read records from rabbitmq instance up until location.offset(); POST them to endpoint
  }

  @Override
  public void close() throws Exception {

  }
}
