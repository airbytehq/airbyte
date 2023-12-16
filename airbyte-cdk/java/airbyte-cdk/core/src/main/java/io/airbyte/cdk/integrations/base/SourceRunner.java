/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.util.concurrent.ConcurrentStreamConsumer;
import io.airbyte.commons.stream.StreamStatusUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SourceRunner extends IntegrationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceRunner.class);

  public SourceRunner(final Source source) {
    super(new IntegrationCliParser(), Destination::defaultOutputRecordCollector, null, source);
  }

  @VisibleForTesting
  SourceRunner(final IntegrationCliParser cliParser,
               final Consumer<AirbyteMessage> outputRecordCollector,
               final Source source) {
    super(cliParser, outputRecordCollector, null, source);
  }

  @VisibleForTesting
  SourceRunner(final IntegrationCliParser cliParser,
               final Consumer<AirbyteMessage> outputRecordCollector,
               final Source source,
               final JsonSchemaValidator jsonSchemaValidator) {
    super(cliParser, outputRecordCollector, null, source, jsonSchemaValidator);
  }

  @Override
  protected void check(IntegrationConfig parsed) throws Exception {
    final JsonNode config = parseConfig(parsed.getConfigPath());
    check(config);
  }

  @Override
  protected void discover(final IntegrationConfig parsed) throws Exception {
    final JsonNode config = parseConfig(parsed.getConfigPath());
    validateConfig(integration.spec().getConnectionSpecification(), config, "DISCOVER");
    outputRecordCollector.accept(new AirbyteMessage().withType(Type.CATALOG).withCatalog(source.discover(config)));
  }

  protected void read(final IntegrationConfig parsed) throws Exception {
    final JsonNode config = parseConfig(parsed.getConfigPath());
    validateConfig(integration.spec().getConnectionSpecification(), config, "READ");
    final ConfiguredAirbyteCatalog catalog = parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog.class);
    final Optional<JsonNode> stateOptional = parsed.getStatePath().map(IntegrationRunner::parseConfig);
    try {
      if (featureFlags.concurrentSourceStreamRead()) {
        LOGGER.info("Concurrent source stream read enabled.");
        readConcurrent(config, catalog, stateOptional);
      } else {
        readSerial(config, catalog, stateOptional);
      }
    } finally {
      if (source instanceof AutoCloseable) {
        ((AutoCloseable) source).close();
      }
    }
  }

  @Override
  protected void write(IntegrationConfig parsed) throws Exception {
    throw new IllegalStateException("Cannot execute write on a source!");
  }

  private void readConcurrent(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final Optional<JsonNode> stateOptional)
      throws Exception {
    final Collection<AutoCloseableIterator<AirbyteMessage>> streams = source.readStreams(config, catalog, stateOptional.orElse(null));

    try (final ConcurrentStreamConsumer streamConsumer = new ConcurrentStreamConsumer(this::consumeFromStream, streams.size())) {
      /*
       * Break the streams into partitions equal to the number of concurrent streams supported by the
       * stream consumer.
       */
      final Integer partitionSize = streamConsumer.getParallelism();
      final List<List<AutoCloseableIterator<AirbyteMessage>>> partitions = Lists.partition(streams.stream().toList(),
          partitionSize);

      // Submit each stream partition for concurrent execution
      partitions.forEach(partition -> {
        streamConsumer.accept(partition);
      });

      // Check for any exceptions that were raised during the concurrent execution
      if (streamConsumer.getException().isPresent()) {
        throw streamConsumer.getException().get();
      }
    } catch (final Exception e) {
      LOGGER.error("Unable to perform concurrent read.", e);
      throw e;
    } finally {
      stopOrphanedThreads(EXIT_HOOK,
          INTERRUPT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES,
          EXIT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES);
    }
  }

  private void readSerial(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final Optional<JsonNode> stateOptional) throws Exception {
    try (final AutoCloseableIterator<AirbyteMessage> messageIterator = source.read(config, catalog, stateOptional.orElse(null))) {
      produceMessages(messageIterator, outputRecordCollector);
    } finally {
      stopOrphanedThreads(EXIT_HOOK,
          INTERRUPT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES,
          EXIT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES);
    }
  }

  private void consumeFromStream(final AutoCloseableIterator<AirbyteMessage> stream) {
    try {
      final Consumer<AirbyteMessage> streamStatusTrackingRecordConsumer = StreamStatusUtils.statusTrackingRecordCollector(stream,
          outputRecordCollector, Optional.of(AirbyteTraceMessageUtility::emitStreamStatusTrace));
      produceMessages(stream, streamStatusTrackingRecordConsumer);
    } catch (final Exception e) {
      stream.getAirbyteStream().ifPresent(s -> LOGGER.error("Failed to consume from stream {}.", s, e));
      throw new RuntimeException(e);
    }
  }

  private void produceMessages(final AutoCloseableIterator<AirbyteMessage> messageIterator, final Consumer<AirbyteMessage> recordCollector) {
    messageIterator.getAirbyteStream().ifPresent(s -> LOGGER.debug("Producing messages for stream {}...", s));
    messageIterator.forEachRemaining(recordCollector);
    messageIterator.getAirbyteStream().ifPresent(s -> LOGGER.debug("Finished producing messages for stream {}..."));
  }

}
