/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.printHeapMemoryConsumption;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.writer.BigQueryTableWriter;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDirectUploader {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDirectUploader.class);

  protected final TableId table;
  protected final BigQueryTableWriter writer;
  protected final BigQuery bigQuery;
  protected final BigQueryRecordFormatter recordFormatter;

  BigQueryDirectUploader(final TableId table,
                         final BigQueryTableWriter writer,
                         final BigQuery bigQuery,
                         final BigQueryRecordFormatter recordFormatter) {
    this.table = table;
    this.writer = writer;
    this.bigQuery = bigQuery;
    this.recordFormatter = recordFormatter;
  }

  public void upload(final PartialAirbyteMessage airbyteMessage) {
    try {
      writer.write(recordFormatter.formatRecord(airbyteMessage));
    } catch (final IOException | RuntimeException e) {
      LOGGER.error("Got an error while writing message: {}", e.getMessage(), e);
      LOGGER.error(String.format(
          "Failed to process a message for job: %s",
          writer.toString()));
      printHeapMemoryConsumption();
      throw new RuntimeException(e);
    }
  }

  public void closeAfterPush() {
    try {
      this.writer.close();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public void createRawTable() {
    // Ensure that this table exists.
    final Table rawTable = bigQuery.getTable(table);
    if (rawTable == null) {
      LOGGER.info("Creating raw table {}.", table);
      bigQuery.create(TableInfo.newBuilder(table, StandardTableDefinition.of(BigQueryRecordFormatter.SCHEMA_V2)).build());
    } else {
      LOGGER.info("Found raw table {}.", rawTable.getTableId());
    }
  }

  @Override
  public String toString() {
    return "BigQueryDirectUploader{" +
        "table=" + table.getTable() +
        ", writer=" + writer.getClass() +
        ", recordFormatter=" + recordFormatter.getClass() +
        '}';
  }

}
