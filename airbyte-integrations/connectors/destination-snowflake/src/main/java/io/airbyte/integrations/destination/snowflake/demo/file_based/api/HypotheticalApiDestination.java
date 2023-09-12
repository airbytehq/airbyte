package io.airbyte.integrations.destination.snowflake.demo.file_based.api;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.PlatformStuff;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.RabbitMqDataWriter;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.record_renderer.RecordRenderer;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.nio.charset.StandardCharsets;

public class HypotheticalApiDestination {

  public static void main(final String[] args) throws Exception {
    final ConfiguredAirbyteCatalog inputCatalog = null;
    final JsonNode inputConfig = null;

    final RecordRenderer recordRenderer = record -> Jsons.serialize(record.getData()).getBytes(StandardCharsets.UTF_8);

    final PlatformStuff<RabbitMqDataWriter.RabbitMqStorageLocation> platform = new PlatformStuff<>(
        inputCatalog,
        inputConfig,
        new HttpStreamDestinationFactory(),
        recordRenderer,
        RabbitMqDataWriter::new,
        200 * 1024 * 1024
    );

    platform.doTheSyncThing();
  }
}
