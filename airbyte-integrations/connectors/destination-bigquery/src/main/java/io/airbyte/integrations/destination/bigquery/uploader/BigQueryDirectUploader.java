/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import com.google.cloud.bigquery.*;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.writer.BigQueryTableWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDirectUploader extends AbstractBigQueryUploader<BigQueryTableWriter> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDirectUploader.class);

  public BigQueryDirectUploader(TableId table,
                                TableId tmpTable,
                                BigQueryTableWriter writer,
                                JobInfo.WriteDisposition syncMode,
                                BigQuery bigQuery,
                                BigQueryRecordFormatter recordFormatter) {
    super(table, tmpTable, writer, syncMode, bigQuery, recordFormatter);
  }

  @Override
  protected void uploadData(Consumer<AirbyteMessage> outputRecordCollector, AirbyteMessage lastStateMessage) throws Exception {
    BigQueryUtils.waitForJobFinish(writer.getWriteChannel().getJob());
    super.uploadData(outputRecordCollector, lastStateMessage);
  }

}
