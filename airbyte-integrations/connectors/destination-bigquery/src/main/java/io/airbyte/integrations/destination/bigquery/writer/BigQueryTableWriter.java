/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.writer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.common.base.Charsets;
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

  public BigQueryTableWriter(TableDataWriteChannel writeChannel) {
    LOGGER.error("===================== CREATING WRITER ==========================");
    this.writeChannel = writeChannel;
  }

  @Override
  public void initialize() throws IOException {}

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage) {
    throw new RuntimeException("This write method is not used!");
  }

  @Override
  public void write(JsonNode formattedData) throws IOException {
    writeChannel.write(ByteBuffer.wrap((Jsons.serialize(formattedData) + "\n").getBytes(Charsets.UTF_8)));
  }

  @Override
  public void write(String formattedData) throws IOException {
    writeChannel.write(ByteBuffer.wrap((formattedData + "\n").getBytes(Charsets.UTF_8)));
  }

  @Override
  public void close(boolean hasFailed) throws IOException {
    LOGGER.error("===================== REGULAR CLOSING ==========================");

    this.writeChannel.close();
    if (writeChannel.getJob().getStatus().getError() != null) {
      LOGGER.error("Fail to complete a load job in big query, Job id: " + writeChannel.getJob().getJobId() +
              ", with error: " + writeChannel.getJob().getStatus().getError());
      throw new RuntimeException("Fail to complete a load job in big query, Job id: " + writeChannel.getJob().getJobId() +
              ", with error: " + writeChannel.getJob().getStatus().getError());
    }
  }

  @Override
  public void closeAfterPush() throws IOException {
    LOGGER.error("===================== CLOSING AFTER PUSH ==========================");
    this.writeChannel.close();
    if (writeChannel.getJob().getStatus().getError() != null) {
      LOGGER.error("Fail to complete a load job in big query, Job id: " + writeChannel.getJob().getJobId() +
              ", with error: " + writeChannel.getJob().getStatus().getError());
      throw new RuntimeException("Fail to complete a load job in big query, Job id: " + writeChannel.getJob().getJobId() +
              ", with error: " + writeChannel.getJob().getStatus().getError());
    }
  }

  public TableDataWriteChannel getWriteChannel() {
    return writeChannel;
  }

}
