package io.airbyte.integrations.destination.snowflake.demo.file_based.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.record_renderer.CsvV2RecordRenderer;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.LocalFileDataWriter;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.PlatformStuff;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;

public class SnowflakeDestination {

  public static void main(final String[] args) throws Exception {
    final ConfiguredAirbyteCatalog inputCatalog = null;
    final JsonNode inputConfig = null;

    // Top-level destination code is our usual IOC setup. Instantiate the platform, configure it for
    // this destination, and then run it.
    // Might be a little tricky to wire this up directly within the jvm, but it's the easiest thing to describe
    // and gives us an easy solution for old versions of platform. We could also define a new interface for destinations
    // to implement, and have main() just call that method.
    final PlatformStuff platform = new PlatformStuff(
        inputCatalog,
        inputConfig,
        new SnowflakeStreamDestinationFactory(),
        new CsvV2RecordRenderer(),
        // shrug, this is probably something that platform would provide
        () -> new LocalFileDataWriter("/tmp/default/file/path"),
        // Various destination-specific parameters can be hardcoded here.
        // For example, maybe Snowflake wants 200MB files.
        200 * 1024 * 1024
    );

    platform.doTheSyncThing();
  }
}
