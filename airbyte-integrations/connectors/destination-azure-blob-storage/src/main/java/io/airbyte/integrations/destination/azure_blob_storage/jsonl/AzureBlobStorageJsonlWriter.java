/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.jsonl;

import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriter;
import io.airbyte.integrations.destination.azure_blob_storage.writer.BaseAzureBlobStorageWriter;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.BufferedOutputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageJsonlWriter extends BaseAzureBlobStorageWriter implements
    AzureBlobStorageWriter {

  protected static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageJsonlWriter.class);

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();

  private BufferedOutputStream blobOutputStream;

  private PrintWriter printWriter;

  private int replicatedBytes;

  private int sequence;

  public AzureBlobStorageJsonlWriter(final AzureBlobStorageDestinationConfig config,
                                     final AppendBlobClient appendBlobClient,
                                     final ConfiguredAirbyteStream configuredStream) {
    super(config, appendBlobClient, configuredStream);
    // at this moment we already receive appendBlobClient initialized
    this.blobOutputStream = new BufferedOutputStream(appendBlobClient.getBlobOutputStream(), config.getOutputStreamBufferSize());
    // layered buffered streams/writers on multiple levels might not bring any benefits
    // since PrintWriter already uses BufferedWriter behind the scenes
    this.printWriter = new PrintWriter(blobOutputStream, false, StandardCharsets.UTF_8);
    this.replicatedBytes = 0;
    this.sequence = 0;
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage) {
    final ObjectNode json = MAPPER.createObjectNode();
    json.put(JavaBaseConstants.COLUMN_NAME_AB_ID, id.toString());
    json.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt());
    json.set(JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getData());
    // inefficient way to calculate correct size in bytes.
    // depending on char encoding something similar can be achieved with str.length() * N
    String jsonRecord = Jsons.serialize(json);
    int recordSize = jsonRecord.getBytes(StandardCharsets.UTF_8).length;
    if (config.getBlobSpillSize() > 0 && replicatedBytes + recordSize > config.getBlobSpillSize()) {
      String subBlobName = appendBlobClient.getBlobName().substring(0, appendBlobClient.getBlobName().length() - 1);
      String blobName = subBlobName + (sequence++);

      final SpecializedBlobClientBuilder specializedBlobClientBuilder =
          AzureBlobStorageDestinationConfig.createSpecializedBlobClientBuilder(config);

      final AppendBlobClient appendBlobClient = specializedBlobClientBuilder
          .blobName(blobName)
          .buildAppendBlobClient();

      this.reinitAppendBlobClient(appendBlobClient);

      this.blobOutputStream =
          new BufferedOutputStream(this.appendBlobClient.getBlobOutputStream(), config.getOutputStreamBufferSize());

      // force flush of records
      this.printWriter.close();
      this.printWriter = new PrintWriter(blobOutputStream, false, StandardCharsets.UTF_8);

      this.printWriter.println(jsonRecord);

      replicatedBytes = 0;
      replicatedBytes += recordSize;
    } else {
      this.printWriter.println(jsonRecord);
      replicatedBytes += recordSize;
    }
    LOGGER.info("Replicated bytes to destination {}", replicatedBytes);
  }

  @Override
  protected void closeWhenSucceed() {
    // this would also close the blobOutputStream
    printWriter.close();
  }

  @Override
  protected void closeWhenFail() {
    // this would also close the blobOutputStream
    printWriter.close();
  }

}
