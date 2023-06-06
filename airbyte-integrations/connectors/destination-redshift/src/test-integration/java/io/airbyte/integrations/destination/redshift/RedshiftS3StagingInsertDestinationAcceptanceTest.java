/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.integrations.destination_async.AsyncStreamConsumer;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

public class RedshiftS3StagingInsertDestinationAcceptanceTest extends RedshiftStagingS3DestinationAcceptanceTest {

  public JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config_staging.json")));
  }

  @Test
  void testWriteRedshiftInternal() {
    final JsonNode config = getStaticConfig();
    final SerializedAirbyteMessageConsumer consumer = new RedshiftStagingS3Destination()
        .getSerializedMessageConsumer(config, new ConfiguredAirbyteCatalog(), null);
    assertEquals(AsyncStreamConsumer.class, consumer.getClass());
  }

}
