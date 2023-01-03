/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import static com.amazonaws.util.StringUtils.UTF8;

import com.google.cloud.bigquery.*;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;

public class GcsCsvBigQueryUploader extends AbstractGscBigQueryUploader<GcsCsvWriter> {

  public GcsCsvBigQueryUploader(TableId table,
                                TableId tmpTable,
                                GcsCsvWriter writer,
                                JobInfo.WriteDisposition syncMode,
                                GcsDestinationConfig gcsDestinationConfig,
                                BigQuery bigQuery,
                                boolean isKeepFilesInGcs,
                                BigQueryRecordFormatter recordFormatter) {
    super(table, tmpTable, writer, syncMode, gcsDestinationConfig, bigQuery, isKeepFilesInGcs, recordFormatter);
  }

  @Override
  protected LoadJobConfiguration getLoadConfiguration() {
    final var csvOptions = CsvOptions.newBuilder().setEncoding(UTF8).setSkipLeadingRows(1).build();

    return LoadJobConfiguration.builder(tmpTable, writer.getFileLocation())
        .setFormatOptions(csvOptions)
        .setSchema(recordFormatter.getBigQuerySchema())
        .setWriteDisposition(syncMode)
        .build();
  }

}
