/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.TableDefinition;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.ParsedCatalog;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Record Consumer used for STANDARD INSERTS
 */
public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  /**
   * Incredibly hacky record to get allow us to write raw tables to one namespace, and final tables to a different namespace.
   * <p>
   * This is effectively just {@link io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair} but with separate namespaces for raw and final.
   * We're not adding a new field there because it's declared in protocol-models, and is painful to modify.
   */
  public record StreamWriteTargets(String finalNamespace, String rawNamespace, String name) {

    public static StreamWriteTargets fromRecordMessage(AirbyteRecordMessage msg, String finalNamespace) {
      return new StreamWriteTargets(finalNamespace, msg.getNamespace(), msg.getStream());
    }

    public static StreamWriteTargets fromAirbyteStream(AirbyteStream stream, String finalNamespace) {
      return new StreamWriteTargets(finalNamespace, stream.getNamespace(), stream.getName());
    }
  }

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);
  public static final int RECORDS_PER_TYPING_AND_DEDUPING_BATCH = 10_000;

  private final Map<StreamWriteTargets, AbstractBigQueryUploader<?>> uploaderMap;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final String datasetId;
  private final BigQuerySqlGenerator sqlGenerator;
  private final BigQueryDestinationHandler destinationHandler;
  private AirbyteMessage lastStateMessage = null;
  // This is super hacky, but in async land we don't need to make this decision at all. We'll just run T+D whenever we commit raw data.
  private final AtomicLong recordsSinceLastTDRun = new AtomicLong(0);
  private final ParsedCatalog<StandardSQLTypeName> catalog;
  private final boolean use1s1t;
  private final String rawNamespaceOverride;

  public BigQueryRecordConsumer(final Map<StreamWriteTargets, AbstractBigQueryUploader<?>> uploaderMap,
                                final Consumer<AirbyteMessage> outputRecordCollector,
                                final String datasetId,
                                final BigQuerySqlGenerator sqlGenerator,
                                final BigQueryDestinationHandler destinationHandler,
                                final ParsedCatalog<StandardSQLTypeName> catalog,
                                final boolean use1s1t, final String rawNamespaceOverride) {
    this.uploaderMap = uploaderMap;
    this.outputRecordCollector = outputRecordCollector;
    this.datasetId = datasetId;
    this.sqlGenerator = sqlGenerator;
    this.destinationHandler = destinationHandler;
    this.catalog = catalog;
    this.use1s1t = use1s1t;
    this.rawNamespaceOverride = rawNamespaceOverride;

    LOGGER.info("Got parsed catalog {}", catalog);
    LOGGER.info("Got canonical stream IDs {}", uploaderMap.keySet());
  }

  @Override
  protected void startTracked() throws InterruptedException {
    // todo (cgardens) - move contents of #write into this method.

    // For each stream, make sure that its corresponding final table exists.
    if (use1s1t) {
      for (StreamConfig<StandardSQLTypeName> stream : catalog.streams()) {
        final Optional<TableDefinition> existingTable = destinationHandler.findExistingTable(stream.id());
        if (existingTable.isEmpty()) {
          destinationHandler.execute(sqlGenerator.createTable(stream));
        } else {
          destinationHandler.execute(sqlGenerator.alterTable(stream, existingTable.get()));
        }
      }
    }
  }

  /**
   * Processes STATE and RECORD {@link AirbyteMessage} with all else logged as unexpected
   *
   * <li>For STATE messages emit messages back to the platform</li>
   * <li>For RECORD messages upload message to associated Airbyte Stream. This means that RECORDS will
   * be associated with their respective streams when more than one record exists</li>
   *
   * @param message {@link AirbyteMessage} to be processed
   */
  @Override
  public void acceptTracked(final AirbyteMessage message) throws InterruptedException {
    if (message.getType() == Type.STATE) {
      lastStateMessage = message;
      outputRecordCollector.accept(message);
    } else if (message.getType() == Type.RECORD) {
      if (StringUtils.isEmpty(message.getRecord().getNamespace())) {
        message.getRecord().setNamespace(datasetId);
      }
      String finalNamespace = message.getRecord().getNamespace();
      if (use1s1t) {
        message.getRecord().setNamespace(rawNamespaceOverride);
      }
      processRecord(finalNamespace, message);
    } else {
      LOGGER.warn("Unexpected message: {}", message.getType());
    }
  }

  /**
   * Processes {@link io.airbyte.protocol.models.AirbyteRecordMessage} by writing Airbyte stream data to Big Query Writer
   *
   * @param message record to be written
   */
  private void processRecord(final String finalNamespace, final AirbyteMessage message) throws InterruptedException {
    final var streamWriteTargets = StreamWriteTargets.fromRecordMessage(message.getRecord(), finalNamespace);
    uploaderMap.get(streamWriteTargets).upload(message);

    // This is just modular arithmetic written in a complicated way. We want to run T+D every RECORDS_PER_TYPING_AND_DEDUPING_BATCH records.
    // TODO this counter should be per stream, not global.
    if (recordsSinceLastTDRun.getAndUpdate(l -> (l + 1) % RECORDS_PER_TYPING_AND_DEDUPING_BATCH) == RECORDS_PER_TYPING_AND_DEDUPING_BATCH - 1) {
      doTypingAndDeduping(streamWriteTargets);
    }
  }

  @Override
  public void close(final boolean hasFailed) {
    LOGGER.info("Started closing all connections");
    final List<Exception> exceptionsThrown = new ArrayList<>();
    uploaderMap.forEach((streamWriteTargets, uploader) -> {
      try {
        uploader.close(hasFailed, outputRecordCollector, lastStateMessage);
        doTypingAndDeduping(streamWriteTargets);
      } catch (final Exception e) {
        exceptionsThrown.add(e);
        LOGGER.error("Exception while closing uploader {}", uploader, e);
      }
    });
    if (!exceptionsThrown.isEmpty()) {
      throw new RuntimeException(String.format("Exceptions thrown while closing consumer: %s", Strings.join(exceptionsThrown, "\n")));
    }
  }

  private void doTypingAndDeduping(final StreamWriteTargets streamWriteTargets) throws InterruptedException {
    if (use1s1t) {
      LOGGER.info("Attempting typing and deduping for {}", streamWriteTargets);
      final StreamConfig<StandardSQLTypeName> stream = catalog.streams()
          .stream()
          .filter(s -> s.id().originalName().equals(streamWriteTargets.name()) && s.id()
              .originalNamespace()
              .equals(streamWriteTargets.finalNamespace()))
          .findFirst()
          // Assume that if we're trying to do T+D on a stream, that stream exists in the catalog.
          .get();
      // TODO generate a suffix for full refresh overwrite syncs
      final String sql = sqlGenerator.updateTable("", stream);
      destinationHandler.execute(sql);
    }
  }

}
