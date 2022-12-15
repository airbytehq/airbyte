/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import com.google.cloud.bigquery.*;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.avro.GcsAvroWriter;

public class GcsAvroBigQueryUploader extends AbstractGscBigQueryUploader<GcsAvroWriter> {

  public GcsAvroBigQueryUploader(TableId table,
                                 TableId tmpTable,
                                 GcsAvroWriter writer,
                                 JobInfo.WriteDisposition syncMode,
                                 GcsDestinationConfig gcsDestinationConfig,
                                 BigQuery bigQuery,
                                 boolean isKeepFilesInGcs,
                                 BigQueryRecordFormatter recordFormatter) {
    super(table, tmpTable, writer, syncMode, gcsDestinationConfig, bigQuery, isKeepFilesInGcs, recordFormatter);
  }

  @Override
  protected LoadJobConfiguration getLoadConfiguration() {
    return LoadJobConfiguration.builder(tmpTable, writer.getFileLocation()).setFormatOptions(FormatOptions.avro())
        .setSchema(recordFormatter.getBigQuerySchema())
        .setWriteDisposition(syncMode)
        .setUseAvroLogicalTypes(true)
        .build();
  }

}
