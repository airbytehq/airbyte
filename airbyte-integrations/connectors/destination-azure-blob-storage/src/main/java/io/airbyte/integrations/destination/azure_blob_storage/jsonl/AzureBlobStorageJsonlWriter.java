/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.jsonl;

import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.BlobOutputStream;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriter;
import io.airbyte.integrations.destination.azure_blob_storage.writer.BaseAzureBlobStorageWriter;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageJsonlWriter extends BaseAzureBlobStorageWriter implements
    AzureBlobStorageWriter {

  protected static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageJsonlWriter.class);

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();
  private static final ObjectWriter WRITER = MAPPER.writer();

  private final BlobOutputStream blobOutputStream;
  private final PrintWriter printWriter;

  public AzureBlobStorageJsonlWriter(AzureBlobStorageDestinationConfig config,
                                     AppendBlobClient appendBlobClient,
                                     ConfiguredAirbyteStream configuredStream,
                                     boolean isNewlyCreatedBlob) {
    super(config, appendBlobClient, configuredStream);
    // at this moment we already receive appendBlobClient initialized
    this.blobOutputStream = appendBlobClient.getBlobOutputStream();
    this.printWriter = new PrintWriter(blobOutputStream, true, StandardCharsets.UTF_8);
  }

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage) {
    ObjectNode json = MAPPER.createObjectNode();
    json.put(JavaBaseConstants.COLUMN_NAME_AB_ID, id.toString());
    json.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt());
    json.set(JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getData());
    printWriter.println(Jsons.serialize(json));
  }

  @Override
  protected void closeWhenSucceed() throws IOException {
    // this would also close the blobOutputStream
    printWriter.close();
  }

  @Override
  protected void closeWhenFail() throws IOException {
    // this would also close the blobOutputStream
    printWriter.close();
  }

}
