package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer;

import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.DataWriter;
import java.io.IOException;
import org.apache.commons.io.function.IOConsumer;

// basically identical to LocalDataWriter, but writes to GCS instead of FileOutputStream
public class GcsDataWriter implements DataWriter {
  @Override
  public String getCurrentFilename() {
    return null;
  }

  @Override
  public void roll() throws IOException {

  }

  @Override
  public IOConsumer<byte[]> getCurrentOutputStream() {
    return null;
  }
}
