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

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Predicate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class InfiniteFeedSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(InfiniteFeedSource.class);

  public static final AirbyteCatalog CATALOG = CatalogHelpers.createAirbyteCatalog(
      "data",
      Field.of("column1", JsonSchemaPrimitive.STRING));

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteCatalog discover(JsonNode config) {
    return Jsons.clone(CATALOG);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) {
    final Predicate<Long> anotherRecordPredicate =
        config.has("max_records") ? recordNumber -> recordNumber < config.get("max_records").asLong() : recordNumber -> true;

    final AtomicLong i = new AtomicLong();

    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      @Override
      protected AirbyteMessage computeNext() {
        if (anotherRecordPredicate.test(i.get())) {
          i.incrementAndGet();
          LOGGER.info("source emitting record {}:", i.get());
          return new AirbyteMessage()
              .withType(Type.RECORD)
              .withRecord(new AirbyteRecordMessage()
                  .withStream("data")
                  .withEmittedAt(Instant.now().toEpochMilli())
                  .withData(Jsons.jsonNode(ImmutableMap.of("column1", i))));
        } else {
          return endOfData();
        }
      }

    });
  }

}
