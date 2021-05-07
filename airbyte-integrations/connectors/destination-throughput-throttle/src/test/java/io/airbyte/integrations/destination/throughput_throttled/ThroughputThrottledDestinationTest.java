package io.airbyte.integrations.destination.throughput_throttled;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.time.Instant;
import org.junit.jupiter.api.Test;

public class ThroughputThrottledDestinationTest {
  @Test
  void test () throws Exception {
    final AirbyteMessageConsumer consumer = new ThroughputThrottledDestination()
        .getConsumer(Jsons.jsonNode(ImmutableMap.of("millis_per_record", 10)), null);

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
