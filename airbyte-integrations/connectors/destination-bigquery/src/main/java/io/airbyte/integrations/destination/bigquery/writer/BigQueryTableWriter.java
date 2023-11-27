/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.writer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.common.base.Charsets;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.destination.s3.writer.DestinationWriter;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryTableWriter implements DestinationWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryTableWriter.class);

  private final TableDataWriteChannel writeChannel;

  public BigQueryTableWriter(final TableDataWriteChannel writeChannel) {
    this.writeChannel = writeChannel;
  }

  @Override
  public void initialize() throws IOException {}

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage) {
    throw new RuntimeException("This write method is not used!");
  }

  @Override
  public void write(final JsonNode formattedData) throws IOException {
    writeChannel.write(ByteBuffer.wrap((Jsons.serialize(formattedData) + "\n").getBytes(Charsets.UTF_8)));
  }

  @Override
  public void write(final String formattedData) throws IOException {
    writeChannel.write(ByteBuffer.wrap((formattedData + "\n").getBytes(Charsets.UTF_8)));
  }

  @Override
  public void close(final boolean hasFailed) throws IOException {
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

  public TableDataWriteChannel getWriteChannel() {
    return writeChannel;
  }

}
