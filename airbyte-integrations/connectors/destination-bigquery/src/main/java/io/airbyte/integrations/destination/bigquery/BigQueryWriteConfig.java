/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;

class BigQueryWriteConfig {

  private final TableId table;
  private final TableId tmpTable;
  private final TableDataWriteChannel writer;
  private final WriteDisposition syncMode;
  private final Schema schema;
  private final GcsCsvWriter gcsCsvWriter;
  private final GcsDestinationConfig gcsDestinationConfig;

  BigQueryWriteConfig(TableId table,
                      TableId tmpTable,
                      TableDataWriteChannel writer,
                      WriteDisposition syncMode,
                      Schema schema,
                      GcsCsvWriter gcsCsvWriter,
                      GcsDestinationConfig gcsDestinationConfig) {
    this.table = table;
    this.tmpTable = tmpTable;
    this.writer = writer;
    this.syncMode = syncMode;
    this.schema = schema;
    this.gcsCsvWriter = gcsCsvWriter;
    this.gcsDestinationConfig = gcsDestinationConfig;
  }

  public TableId getTable() {
    return table;
  }

  public TableId getTmpTable() {
    return tmpTable;
  }

  public TableDataWriteChannel getWriter() {
    return writer;
  }

  public WriteDisposition getSyncMode() {
    return syncMode;
  }

  public Schema getSchema() {
    return schema;
  }

  public GcsCsvWriter getGcsCsvWriter() {
    return gcsCsvWriter;
  }

  public GcsDestinationConfig getGcsDestinationConfig() {
    return gcsDestinationConfig;
  }

}
