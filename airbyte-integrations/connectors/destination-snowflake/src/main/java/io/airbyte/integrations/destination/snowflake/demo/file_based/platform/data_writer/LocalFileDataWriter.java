package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.UUID;
import org.apache.commons.io.function.IOConsumer;

public class LocalFileDataWriter implements DataWriter<LocalFileDataWriter.LocalFileLocation> {

  private final String path;
  private String filename;
  private OutputStream out;

  public LocalFileDataWriter(final String path) {
    this.path = path;
  }

  @Override
  public LocalFileLocation getCurrentLocation() {
    return new LocalFileLocation(path + "/" + filename);
  }

  @Override
  public void roll() throws IOException {
    if (out != null) {
      out.close();
    }
    filename = UUID.randomUUID().toString();
    out = new FileOutputStream(path + "/" + filename);
  }

  @Override
  public IOConsumer<byte[]> getCurrentOutputStream() {
    return bytes -> out.write(bytes);
  }

  public record LocalFileLocation(String path) implements StorageLocation {

  }
}
