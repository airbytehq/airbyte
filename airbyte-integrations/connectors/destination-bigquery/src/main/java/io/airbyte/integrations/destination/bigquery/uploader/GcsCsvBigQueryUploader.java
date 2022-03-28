/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import static com.amazonaws.util.StringUtils.UTF8;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.CsvOptions;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.LoadJobConfiguration;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.integrations.destination.s3.csv.CsvSheetGenerator;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.QuoteMode;

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

  public static CSVFormat getCsvFormat(final CsvSheetGenerator csvSheetGenerator) {
    return CSVFormat.DEFAULT.withQuoteMode(QuoteMode.ALL)
        .withHeader(csvSheetGenerator.getHeaderRow().toArray(new String[0]));
  }

  @Override
  protected LoadJobConfiguration getLoadConfiguration() {
    final var csvOptions = CsvOptions.newBuilder().setEncoding(UTF8).setSkipLeadingRows(1).build();

    return LoadJobConfiguration.builder(tmpTable, writer.getFileLocation())
        .setFormatOptions(csvOptions)
        .setSchema(recordFormatter.getBigQuerySchema())
        // always append to the tmp table, because we may upload the data in small batches
        .setWriteDisposition(WriteDisposition.WRITE_APPEND)
        .build();
  }

}
