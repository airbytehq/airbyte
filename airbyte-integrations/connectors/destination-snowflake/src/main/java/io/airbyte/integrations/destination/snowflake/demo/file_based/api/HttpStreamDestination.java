package io.airbyte.integrations.destination.snowflake.demo.file_based.api;

import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestination;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.StorageLocation;

public class HttpStreamDestination implements StreamDestination {
  private final String endpoint;

  @Override
  public void setup() throws Exception {

  }

  @Override
  public void upload(final StorageLocation id, final int numRecords, final int numBytes) throws Exception {
    if (id instanceof StorageLocation.RabbitMq) {
      // read records from rabbitmq instance, POST them to endpoint
    } else if (id instanceof StorageLocation.LocalFileLocation) {
      // read lines out of a file, POST them to endpoint
    } else {
      // etc.
    }
  }

  @Override
  public void close() throws Exception {

  }
}
