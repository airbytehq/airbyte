package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer;

import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.DataWriter;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.UUID;
import org.apache.commons.io.function.IOConsumer;

public class LocalFileDataWriter implements DataWriter {

  private final String path;
  private String filename;
  private OutputStream out;

  public LocalFileDataWriter(String path) {
    this.path = path;
  }

  @Override
  public String getCurrentFilename() {
    return null;
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
}
