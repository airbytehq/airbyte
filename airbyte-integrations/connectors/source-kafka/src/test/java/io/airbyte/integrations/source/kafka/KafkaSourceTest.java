/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import static org.junit.jupiter.api.Assertions.assertInstanceOf;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.kafka.format.AvroFormat;
import io.airbyte.integrations.source.kafka.format.KafkaFormat;
import java.io.IOException;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import org.junit.jupiter.api.Test;

public class KafkaSourceTest {

  @Test
  public void testAvroformat() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
    final KafkaFormat kafkaFormat = KafkaFormatFactory.getFormat(configJson);
//    AutoCloseableIterator<AirbyteMessage> message = kafkaFormat.read();
//    AirbyteMessage mesag = message.next();
    assertInstanceOf(AvroFormat.class, kafkaFormat);
  }

//  @Test
//  public void testAvroMessage() throws Exception {
//    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
//    final Source source = new KafkaSource();
//    source.discover(configJson);
//
//  }





}
