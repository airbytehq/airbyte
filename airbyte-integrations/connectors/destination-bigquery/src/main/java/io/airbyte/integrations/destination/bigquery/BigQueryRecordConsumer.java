/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator.StreamId;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Record Consumer used for STANDARD INSERTS
 */
public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  public static final String OVERWRITE_TABLE_SUFFIX = "_airbyte_tmp";

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final BigQuery bigquery;
  private final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final String defaultDatasetId;
  private final BigQuerySqlGenerator sqlGenerator;
  private final BigQueryDestinationHandler destinationHandler;
  private AirbyteMessage lastStateMessage = null;

  private final TypeAndDedupeOperationValve streamTDValve = new TypeAndDedupeOperationValve();
  private final ParsedCatalog catalog;
  private final boolean use1s1t;
  private final Map<StreamId, String> overwriteStreamsWithTmpTable;

  public BigQueryRecordConsumer(final BigQuery bigquery,
                                final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap,
                                final Consumer<AirbyteMessage> outputRecordCollector,
                                final String defaultDatasetId,
                                final BigQuerySqlGenerator sqlGenerator,
                                final BigQueryDestinationHandler destinationHandler,
                                final ParsedCatalog catalog) {
    this.bigquery = bigquery;
    this.uploaderMap = uploaderMap;
    this.outputRecordCollector = outputRecordCollector;
    this.defaultDatasetId = defaultDatasetId;
    this.sqlGenerator = sqlGenerator;
    this.destinationHandler = destinationHandler;
    this.catalog = catalog;
    this.overwriteStreamsWithTmpTable = new HashMap<>();

    this.use1s1t = TypingAndDedupingFlag.isDestinationV2();

    LOGGER.info("Got parsed catalog {}", catalog);
    LOGGER.info("Got canonical stream IDs {}", uploaderMap.keySet());
  }

  @Override
  protected void startTracked() throws InterruptedException {
    // todo (cgardens) - move contents of #write into this method.

    if (use1s1t) {
      // TODO extract common logic with GCS record consumer + extract into a higher level class
      // For each stream, make sure that its corresponding final table exists.
      for (final StreamConfig stream : catalog.streams()) {
        final Optional<TableDefinition> existingTable = destinationHandler.findExistingTable(stream.id());
        if (existingTable.isEmpty()) {
          destinationHandler.execute(sqlGenerator.createTable(stream, ""));
          if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
            // We're creating this table for the first time. Write directly into it.
            overwriteStreamsWithTmpTable.put(stream.id(), "");
          }
        } else {
          destinationHandler.execute(sqlGenerator.alterTable(stream, existingTable.get()));
          if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
            final BigInteger rowsInFinalTable = bigquery.getTable(TableId.of(stream.id().finalNamespace(), stream.id().finalName())).getNumRows();
            if (new BigInteger("0").equals(rowsInFinalTable)) {
              // The table already exists but is empty. We'll load data incrementally.
              // (this might be because the user ran a reset, which creates an empty table)
              overwriteStreamsWithTmpTable.put(stream.id(), "");
            } else {
              // We're working with an existing table. Write into a tmp table. We'll overwrite the table at the
              // end of the sync.
              overwriteStreamsWithTmpTable.put(stream.id(), OVERWRITE_TABLE_SUFFIX);
            }
          }
        }
      }

      // For streams in overwrite mode, truncate the raw table and create a tmp table.
      // non-1s1t syncs actually overwrite the raw table at the end of the sync, so we only do this in
      // 1s1t mode.
      for (final StreamConfig stream : catalog.streams()) {
        LOGGER.info("Stream {} has sync mode {}", stream.id(), stream.destinationSyncMode());
        final String suffix = overwriteStreamsWithTmpTable.get(stream.id());
        if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE && suffix != null && !suffix.isEmpty()) {
          // drop+recreate the raw table
          final TableId rawTableId = TableId.of(stream.id().rawNamespace(), stream.id().rawName());
          bigquery.delete(rawTableId);
          BigQueryUtils.createPartitionedTableIfNotExists(bigquery, rawTableId, DefaultBigQueryRecordFormatter.SCHEMA_V2);

          // create the tmp final table
          destinationHandler.execute(sqlGenerator.createTable(stream, suffix));
        }
      }

      uploaderMap.forEach((streamId, uploader) -> {
        uploader.createRawTable();
      });
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
        message.getRecord().setNamespace(defaultDatasetId);
      }
      processRecord(message);
    } else {
      LOGGER.warn("Unexpected message: {}", message.getType());
    }
  }

  /**
   * Processes {@link io.airbyte.protocol.models.AirbyteRecordMessage} by writing Airbyte stream data
   * to Big Query Writer
   *
   * @param message record to be written
   */
  private void processRecord(final AirbyteMessage message) throws InterruptedException {
    final var streamId = AirbyteStreamNameNamespacePair.fromRecordMessage(message.getRecord());
    uploaderMap.get(streamId).upload(message);
    if (!streamTDValve.containsKey(streamId)) {
      streamTDValve.addStream(streamId);
    } else if (streamTDValve.readyToTypeAndDedupeWithAdditionalRecord(streamId)) {
      doTypingAndDeduping(catalog.getStream(streamId.getNamespace(), streamId.getName()));
      streamTDValve.updateTimeAndIncreaseInterval(streamId);
    }
  }

  @Override
  public void close(final boolean hasFailed) {
    LOGGER.info("Started closing all connections");
    final List<Exception> exceptionsThrown = new ArrayList<>();
    uploaderMap.forEach((streamId, uploader) -> {
      try {
        uploader.close(hasFailed, outputRecordCollector, lastStateMessage);
        if (use1s1t) {
          LOGGER.info("Attempting typing and deduping for {}", streamId);
          final StreamConfig streamConfig = catalog.getStream(streamId.getNamespace(), streamId.getName());
          doTypingAndDeduping(streamConfig);
          if (streamConfig.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
            LOGGER.info("Overwriting final table with tmp table");
            // We're at the end of the sync. Move the tmp table to the final table.
            final Optional<String> overwriteFinalTable =
                sqlGenerator.overwriteFinalTable(overwriteStreamsWithTmpTable.get(streamConfig.id()), streamConfig);
            if (overwriteFinalTable.isPresent()) {
              destinationHandler.execute(overwriteFinalTable.get());
            }
          }
        }
      } catch (final Exception e) {
        exceptionsThrown.add(e);
        LOGGER.error("Exception while closing uploader {}", uploader, e);
      }
    });
    if (!exceptionsThrown.isEmpty()) {
      throw new RuntimeException(String.format("Exceptions thrown while closing consumer: %s", Strings.join(exceptionsThrown, "\n")));
    }
  }

  private void doTypingAndDeduping(final StreamConfig stream) throws InterruptedException {
    if (use1s1t) {
      final String suffix;
      suffix = overwriteStreamsWithTmpTable.getOrDefault(stream.id(), "");
      final String sql = sqlGenerator.updateTable(suffix, stream);
      destinationHandler.execute(sql);
    }
  }

}
