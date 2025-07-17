/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.staging;

import io.airbyte.cdk.integrations.destination.record_buffer.BaseSerializedBuffer;
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreSqlGenerator;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("try")
public class SingleStoreCsvSerializedBuffer extends BaseSerializedBuffer {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreCsvSerializedBuffer.class);
  private CSVPrinter csvPrinter;

  @SuppressWarnings("this-escape")
  public SingleStoreCsvSerializedBuffer(@NotNull BufferStorage bufferStorage) {
    super(bufferStorage);
    this.withCompression(false);
  }

  @Override
  protected void closeWriter() throws IOException {
    if (csvPrinter != null) {
      csvPrinter.close();
    } else {
      LOGGER.warn("Trying to close but no printer is initialized.");
    }
  }

  @Override
  protected void initWriter(@NotNull OutputStream outputStream) throws Exception {
    csvPrinter = new CSVPrinter(new PrintWriter(outputStream, true, StandardCharsets.UTF_8), CSVFormat.DEFAULT);
  }

  @Deprecated
  @Override
  protected void writeRecord(@NotNull AirbyteRecordMessage airbyteRecordMessage) throws IOException {
    csvPrinter.printRecord(getDataRow(UUID.randomUUID(), airbyteRecordMessage));
  }

  @Override
  protected void writeRecord(@NotNull String recordString, @NotNull String airbyteMetaString, long generationId, long emittedAt) throws IOException {
    csvPrinter.printRecord(getDataRow(UUID.randomUUID(), recordString, emittedAt, airbyteMetaString, generationId));
  }

  private List<Object> getDataRow(UUID id, AirbyteRecordMessage recordMessage) {
    return getDataRow(id, Jsons.serialize(recordMessage.getData()), recordMessage.getEmittedAt(), Jsons.serialize(recordMessage.getMeta()),
        // Legacy code. Default to generation 0.
        0L);
  }

  private List<Object> getDataRow(UUID id, String formattedString, Long emittedAt, String formattedAirbyteMetaString, Long generationId) {
    return List.of(id, convertTimestamp(emittedAt), "", formattedString, formattedAirbyteMetaString, generationId);
  }

  private String convertTimestamp(Long timestamp) {
    return SingleStoreSqlGenerator.TIMESTAMP_FORMATTER.format(Instant.ofEpochMilli(timestamp));
  }

  @Override
  protected void flushWriter() throws IOException {
    if (csvPrinter != null) {
      csvPrinter.flush();
    } else {
      LOGGER.warn("Trying to flush but no printer is initialized.");
    }
  }

}
