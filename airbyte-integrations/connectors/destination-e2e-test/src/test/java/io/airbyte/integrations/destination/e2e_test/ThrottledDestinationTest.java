/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.e2e_test;

import static org.mockito.Mockito.mock;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.time.Instant;
import java.util.Map;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/**
 * This source is designed to be a switch statement for our suite of highly-specific test sourcess.
 */
public class ThrottledDestinationTest {

  @SuppressWarnings("unchecked")
  @Test
  void test() throws Exception {
    Consumer<AirbyteMessage> outputRecordCollector = mock(Consumer.class);
    final AirbyteMessageConsumer consumer = new ThrottledDestination()
        .getConsumer(Jsons.jsonNode(Map.of("millis_per_record", 10)), null, outputRecordCollector);

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
