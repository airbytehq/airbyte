/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import com.google.cloud.bigquery.*;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.writer.BigQueryTableWriter;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.function.Consumer;

public class BigQueryDirectUploader extends AbstractBigQueryUploader<BigQueryTableWriter> {

  public BigQueryDirectUploader(final TableId table,
                                final TableId tmpTable,
                                final BigQueryTableWriter writer,
                                final JobInfo.WriteDisposition syncMode,
                                final BigQuery bigQuery,
                                final BigQueryRecordFormatter recordFormatter) {
    super(table, tmpTable, writer, syncMode, bigQuery, recordFormatter);
  }

  @Override
  protected void uploadData(final Consumer<AirbyteMessage> outputRecordCollector, final AirbyteMessage lastStateMessage) throws Exception {
    BigQueryUtils.waitForJobFinish(writer.getWriteChannel().getJob());
    super.uploadData(outputRecordCollector, lastStateMessage);
  }

}
