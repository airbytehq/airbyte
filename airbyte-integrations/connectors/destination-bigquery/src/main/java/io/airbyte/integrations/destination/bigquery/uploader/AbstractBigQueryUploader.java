/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableId;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.writer.CommonWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.printHeapMemoryConsumption;

public abstract class AbstractBigQueryUploader<T extends CommonWriter> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractBigQueryUploader.class);

  protected final TableId table;
  protected final TableId tmpTable;
  protected final WriteDisposition syncMode;
  protected final Schema schema;
  protected final T writer;
  protected final GcsDestinationConfig gcsDestinationConfig;
  protected final BigQuery bigQuery;

  AbstractBigQueryUploader(final TableId table,
                           final TableId tmpTable,
                           final T writer,
                           final WriteDisposition syncMode,
                           final Schema schema,
                           final GcsDestinationConfig gcsDestinationConfig,
                           final BigQuery bigQuery) {
    this.table = table;
    this.tmpTable = tmpTable;
    this.writer = writer;
    this.syncMode = syncMode;
    this.schema = schema;
    this.gcsDestinationConfig = gcsDestinationConfig;
    this.bigQuery = bigQuery;
  }

  public void upload(AirbyteMessage airbyteMessage) {
    try {
      writer
              .write((formatRecord(airbyteMessage.getRecord())));
    } catch (final IOException | RuntimeException e) {
      LOGGER.error("Got an error while writing message: {}", e.getMessage(), e);
      LOGGER.error(String.format(
              "Failed to process a message for job: \n%s, \nAirbyteMessage: %s",
              writer.toString(),
              airbyteMessage.getRecord()));
      printHeapMemoryConsumption();
      throw new RuntimeException(e);
    }
  }

  protected JsonNode formatRecord(final AirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
    return Jsons.jsonNode(ImmutableMap.of(
            JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
            JavaBaseConstants.COLUMN_NAME_DATA, Jsons.serialize(formattedData),
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt));
  }

  public void close(boolean hasFailed) {
        try {
          LOGGER.info("Closing connector:" + this);
          this.closeWriter(hasFailed);
          LOGGER.info("Closed connector:" + this);
        } catch (final Exception e) {
          LOGGER.error(String.format("Failed to close %s writer, \n details: %s", this, e.getMessage()));
          printHeapMemoryConsumption();
          throw new RuntimeException(e);
        }
  }

  protected abstract void closeWriter(boolean hasFailed) throws Exception;

}
