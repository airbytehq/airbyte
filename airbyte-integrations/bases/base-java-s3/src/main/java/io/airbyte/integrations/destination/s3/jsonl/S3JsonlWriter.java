/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.template.S3FilenameTemplateParameterObject;
import io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory;
import io.airbyte.integrations.destination.s3.writer.BaseS3Writer;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.Timestamp;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3JsonlWriter extends BaseS3Writer implements DestinationFileWriter {

  protected static final Logger LOGGER = LoggerFactory.getLogger(S3JsonlWriter.class);

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();

  private final StreamTransferManager uploadManager;
  private final MultiPartOutputStream outputStream;
  private final PrintWriter printWriter;
  private final String objectKey;
  private final String gcsFileLocation;

  public S3JsonlWriter(final S3DestinationConfig config,
                       final AmazonS3 s3Client,
                       final ConfiguredAirbyteStream configuredStream,
                       final Timestamp uploadTimestamp)
      throws IOException {
    super(config, s3Client, configuredStream);

    final String outputFilename = determineOutputFilename(S3FilenameTemplateParameterObject
        .builder()
        .timestamp(uploadTimestamp)
        .s3Format(S3Format.JSONL)
        .fileExtension(S3Format.JSONL.getFileExtension())
        .fileNamePattern(config.getFileNamePattern())
        .build());
    objectKey = String.join("/", outputPrefix, outputFilename);

    LOGGER.info("Full S3 path for stream '{}': s3://{}/{}", stream.getName(), config.getBucketName(), objectKey);
    gcsFileLocation = String.format("gs://%s/%s", config.getBucketName(), objectKey);

    this.uploadManager = StreamTransferManagerFactory
        .create(config.getBucketName(), objectKey, s3Client)
        .get();
    // We only need one output stream as we only have one input stream. This is reasonably performant.
    this.outputStream = uploadManager.getMultiPartOutputStreams().get(0);
    this.printWriter = new PrintWriter(outputStream, true, StandardCharsets.UTF_8);
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage) {
    final ObjectNode json = MAPPER.createObjectNode();
    json.put(JavaBaseConstants.COLUMN_NAME_AB_ID, id.toString());
    json.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt());
    json.set(JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getData());
    printWriter.println(Jsons.serialize(json));
  }

  @Override
  protected void closeWhenSucceed() {
    printWriter.close();
    outputStream.close();
    uploadManager.complete();
  }

  @Override
  protected void closeWhenFail() {
    printWriter.close();
    outputStream.close();
    uploadManager.abort();
  }

  @Override
  public String getOutputPath() {
    return objectKey;
  }

  @Override
  public String getFileLocation() {
    return gcsFileLocation;
  }

  @Override
  public S3Format getFileFormat() {
    return S3Format.JSONL;
  }

  @Override
  public void write(final JsonNode formattedData) throws IOException {
    printWriter.println(Jsons.serialize(formattedData));
  }

}
