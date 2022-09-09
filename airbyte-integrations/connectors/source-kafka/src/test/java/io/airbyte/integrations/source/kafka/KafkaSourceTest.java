/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import static org.junit.jupiter.api.Assertions.assertInstanceOf;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.kafka.format.AvroFormat;
import io.airbyte.integrations.source.kafka.format.KafkaFormat;
import java.io.IOException;
import org.junit.jupiter.api.Test;

public class KafkaSourceTest {

  @Test
  public void testAvroformat() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
    final KafkaFormat kafkaFormat = KafkaFormatFactory.getFormat(configJson);
    assertInstanceOf(AvroFormat.class, kafkaFormat);
  }

}
