package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer;

import java.io.IOException;
import org.apache.commons.io.function.IOConsumer;

public class RabbitMqDataWriter implements DataWriter<RabbitMqDataWriter.RabbitMqStorageLocation> {

  @Override
  public RabbitMqStorageLocation getCurrentLocation() {
    return null;
  }

  @Override
  public void roll() throws IOException {

  }

  @Override
  public IOConsumer<byte[]> getCurrentOutputStream() {
    return null;
  }

  public record RabbitMqStorageLocation(int offset) implements StorageLocation {
  }
}
