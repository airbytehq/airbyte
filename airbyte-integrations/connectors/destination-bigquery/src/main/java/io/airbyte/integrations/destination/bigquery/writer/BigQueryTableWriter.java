/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.writer;

import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.common.base.Charsets;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import java.io.IOException;
import java.nio.ByteBuffer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public record BigQueryTableWriter(TableDataWriteChannel writeChannel) {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryTableWriter.class);

  public void write(final String formattedData) throws IOException {
    writeChannel.write(ByteBuffer.wrap((formattedData + "\n").getBytes(Charsets.UTF_8)));
  }

  public void close() throws IOException {
    this.writeChannel.close();
    try {
      final Job job = writeChannel.getJob();
      if (job != null && job.getStatus().getError() != null) {
        AirbyteExceptionHandler.addStringForDeinterpolation(job.getEtag());
        throw new RuntimeException("Fail to complete a load job in big query, Job id: " + writeChannel.getJob().getJobId() +
            ", with error: " + writeChannel.getJob().getStatus().getError());
      }
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}
