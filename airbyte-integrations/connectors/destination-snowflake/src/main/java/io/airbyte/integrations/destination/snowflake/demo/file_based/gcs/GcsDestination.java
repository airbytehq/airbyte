package io.airbyte.integrations.destination.snowflake.demo.file_based.gcs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.NoopStreamDestinationFactory;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.PlatformStuff;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.GcsDataWriter;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.record_renderer.CsvV2RecordRenderer;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.record_renderer.RecordRenderer;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;

public class GcsDestination {

  public static void main(final String[] args) throws Exception {
    final ConfiguredAirbyteCatalog inputCatalog = null;
    final JsonNode inputConfig = null;

    final RecordRenderer recordRenderer = switch (inputConfig.get("output_format").asText()) {
      case "CSV" -> new CsvV2RecordRenderer();
      // we could also support avro, etc.
      default -> null;
    };

    final PlatformStuff<GcsDataWriter.GcsFileLocation> platform = new PlatformStuff<>(
        inputCatalog,
        inputConfig,
        // We don't _really_ need to do anything here! Platform will inherently write files to GCS for us.
        // But if we want to e.g. delete existing files for OVERWRITE steams, we would need a custom streamdestination.
        new NoopStreamDestinationFactory(),
        recordRenderer,
        // In reality, we would take the service account key, etc. from inputConfig and pass them into this constructor.
        GcsDataWriter::new,
        200 * 1024 * 1024
    );

    platform.doTheSyncThing();
  }
}
