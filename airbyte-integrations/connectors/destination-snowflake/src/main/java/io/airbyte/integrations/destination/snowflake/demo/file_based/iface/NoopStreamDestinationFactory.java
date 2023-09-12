package io.airbyte.integrations.destination.snowflake.demo.file_based.iface;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.StorageId;
import java.io.File;

public class NoopStreamDestinationFactory implements StreamDestinationFactory {
  @Override
  public void setup(final JsonNode config) {

  }

  @Override
  public StreamDestination build(final StreamConfig stream) {
    return new StreamDestination() {

      @Override
      public void close() throws Exception {

      }

      @Override
      public void setup() throws Exception {

      }

      @Override
      public void upload(final StorageId id, final int numRecords, final int numBytes) throws Exception {

      }
    };
  }

  @Override
  public void close() throws Exception {

  }
}
