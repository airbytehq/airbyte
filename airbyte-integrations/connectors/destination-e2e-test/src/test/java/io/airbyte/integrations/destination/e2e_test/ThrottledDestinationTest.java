/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test;

import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;
import java.util.Collections;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/**
 * This source is designed to be a switch statement for our suite of highly-specific test sources.
 */
public class ThrottledDestinationTest {

  @SuppressWarnings("unchecked")
  @Test
  void test() throws Exception {
    final Consumer<AirbyteMessage> outputRecordCollector = mock(Consumer.class);

    final JsonNode config = Jsons.jsonNode(
        Collections.singletonMap("test_destination", Collections.singletonMap("millis_per_record", 10)));

    final AirbyteMessageConsumer consumer = new ThrottledDestination().getConsumer(config, null, outputRecordCollector);

    consumer.accept(getAnotherRecord());
    consumer.accept(getAnotherRecord());
    consumer.accept(getAnotherRecord());
    consumer.accept(getAnotherRecord());
    consumer.accept(getAnotherRecord());
  }

  private static AirbyteMessage getAnotherRecord() {
    return new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream("data")
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(Jsons.jsonNode(ImmutableMap.of("column1", "contents1 " + Instant.now().toEpochMilli()))));
  }

}
