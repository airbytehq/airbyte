/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.azure.storage.blob.specialized.AppendBlobClient;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.LinkedList;
import java.util.List;

public class AzureBlobStorageJsonlDestinationAcceptanceTest extends
    AzureBlobStorageDestinationAcceptanceTest {

  public AzureBlobStorageJsonlDestinationAcceptanceTest() {
    super(AzureBlobStorageFormat.JSONL);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"JSONL\"\n"
        + "}");
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws IOException {

    final String allSyncedObjects = getAllSyncedObjects(streamName);
    final List<JsonNode> jsonRecords = new LinkedList<>();

    allSyncedObjects.lines().forEach(line -> {
      jsonRecords.add(Jsons.deserialize(line).get(JavaBaseConstants.COLUMN_NAME_DATA));
    });
    return jsonRecords;
  }

  @Override
  protected String getAllSyncedObjects(String streamName) {
    try {
      final List<AppendBlobClient> appendBlobClients = getAppendBlobClient(streamName);
      StringBuilder result = new StringBuilder();
      for (AppendBlobClient appendBlobClient : appendBlobClients) {
        final ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        appendBlobClient.download(outputStream);
        result.append(outputStream.toString(StandardCharsets.UTF_8));
      }
      LOGGER.info("All objects: " + result);
      return result.toString();
    } catch (Exception e) {
      LOGGER.error("No blobs were found for stream with name {}.", streamName);
      return "";
    }
  }

}
