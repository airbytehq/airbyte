/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.Iterators;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Instant;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Optional;
import java.util.Random;
import java.util.concurrent.atomic.AtomicLong;
import javax.annotation.CheckForNull;
import net.jimblackler.jsongenerator.Generator;
import net.jimblackler.jsongenerator.JsonGeneratorException;
import net.jimblackler.jsonschemafriend.Schema;
import net.jimblackler.jsonschemafriend.SchemaStore;

public class ContinuousFeedSource extends BaseConnector implements Source {

  @Override
  public AirbyteConnectionStatus check(final JsonNode jsonConfig) {
    try {
      final ContinuousFeedConfig sourceConfig = new ContinuousFeedConfig(jsonConfig);
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED).withMessage("Source config: " + sourceConfig);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode jsonConfig) throws Exception {
    final ContinuousFeedConfig sourceConfig = new ContinuousFeedConfig(jsonConfig);
    return sourceConfig.getMockCatalog();
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode jsonConfig, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    final ContinuousFeedConfig feedConfig = new ContinuousFeedConfig(jsonConfig);
    final List<Iterator<AirbyteMessage>> iterators = new LinkedList<>();

    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final AtomicLong emittedMessages = new AtomicLong(0);
      final Optional<Long> messageIntervalMs = feedConfig.getMessageIntervalMs();

      final SchemaStore schemaStore = new SchemaStore(true);
      final Schema schema = schemaStore.loadSchemaJson(Jsons.serialize(stream.getStream().getJsonSchema()));
      final Random random = new Random(feedConfig.getSeed());
      final Generator generator = new Generator(ContinuousFeedConstants.MOCK_JSON_CONFIG, schemaStore, random);

      final Iterator<AirbyteMessage> streamIterator = new AbstractIterator<>() {

        @CheckForNull
        @Override
        protected AirbyteMessage computeNext() {

          if (emittedMessages.get() >= feedConfig.getMaxMessages()) {
            return endOfData();
          }

          if (messageIntervalMs.isPresent() && emittedMessages.get() != 0) {
            try {
              Thread.sleep(messageIntervalMs.get());
            } catch (final InterruptedException e) {
              throw new RuntimeException(e);
            }
          }

          final JsonNode data;
          try {
            data = Jsons.jsonNode(generator.generate(schema, ContinuousFeedConstants.MOCK_JSON_MAX_TREE_SIZE));
          } catch (final JsonGeneratorException e) {
            throw new RuntimeException(e);
          }
          emittedMessages.incrementAndGet();
          return new AirbyteMessage()
              .withType(Type.RECORD)
              .withRecord(new AirbyteRecordMessage()
                  .withStream(stream.getStream().getName())
                  .withEmittedAt(Instant.now().toEpochMilli())
                  .withData(data));
        }

      };
      iterators.add(streamIterator);
    }

    return AutoCloseableIterators.fromIterator(Iterators.concat(iterators.iterator()));
  }

}
