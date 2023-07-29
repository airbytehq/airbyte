/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.TableId;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryRecordFormatter;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Record Consumer used for STANDARD INSERTS
 */
public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final BigQuery bigquery;
  private final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final String defaultDatasetId;
  private AirbyteMessage lastStateMessage = null;

  private final TypeAndDedupeOperationValve streamTDValve = new TypeAndDedupeOperationValve();
  private final ParsedCatalog catalog;
  private final boolean use1s1t;
  private final TyperDeduper typerDeduper;

  public BigQueryRecordConsumer(final BigQuery bigquery,
                                final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap,
                                final Consumer<AirbyteMessage> outputRecordCollector,
                                final String defaultDatasetId,
                                TyperDeduper typerDeduper,
                                final ParsedCatalog catalog) {
    this.bigquery = bigquery;
    this.uploaderMap = uploaderMap;
    this.outputRecordCollector = outputRecordCollector;
    this.defaultDatasetId = defaultDatasetId;
    this.typerDeduper = typerDeduper;
    this.catalog = catalog;
    this.use1s1t = TypingAndDedupingFlag.isDestinationV2();

    LOGGER.info("Got parsed catalog {}", catalog);
    LOGGER.info("Got canonical stream IDs {}", uploaderMap.keySet());
  }

  @Override
  protected void startTracked() throws Exception {
    // todo (cgardens) - move contents of #write into this method.

    typerDeduper.prepareFinalTables();
    if (use1s1t) {
      // Set up our raw tables
      uploaderMap.forEach((streamId, uploader) -> {
        StreamConfig stream = catalog.getStream(streamId);
        if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
          // For streams in overwrite mode, truncate the raw table.
          // non-1s1t syncs actually overwrite the raw table at the end of the sync, so we only do this in
          // 1s1t mode.
          final TableId rawTableId = TableId.of(stream.id().rawNamespace(), stream.id().rawName());
          bigquery.delete(rawTableId);
          BigQueryUtils.createPartitionedTableIfNotExists(bigquery, rawTableId, DefaultBigQueryRecordFormatter.SCHEMA_V2);
        } else {
          uploader.createRawTable();
        }
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
  public void acceptTracked(final AirbyteMessage message) throws Exception {
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
  private void processRecord(final AirbyteMessage message) {
    final var streamId = AirbyteStreamNameNamespacePair.fromRecordMessage(message.getRecord());
    uploaderMap.get(streamId).upload(message);
    // We are not doing any incremental typing and de-duping for Standard Inserts, see
    // https://github.com/airbytehq/airbyte/issues/27586
  }

  @Override
  public void close(final boolean hasFailed) throws Exception {
    LOGGER.info("Started closing all connections");
    final List<Exception> exceptionsThrown = new ArrayList<>();
    uploaderMap.forEach((streamId, uploader) -> {
      try {
        uploader.close(hasFailed, outputRecordCollector, lastStateMessage);
        typerDeduper.typeAndDedupe(streamId.getNamespace(), streamId.getName());
      } catch (final Exception e) {
        exceptionsThrown.add(e);
        LOGGER.error("Exception while closing uploader {}", uploader, e);
      }
    });
    typerDeduper.commitFinalTables();
    if (!exceptionsThrown.isEmpty()) {
      throw new RuntimeException(String.format("Exceptions thrown while closing consumer: %s", Strings.join(exceptionsThrown, "\n")));
    }
  }

}
