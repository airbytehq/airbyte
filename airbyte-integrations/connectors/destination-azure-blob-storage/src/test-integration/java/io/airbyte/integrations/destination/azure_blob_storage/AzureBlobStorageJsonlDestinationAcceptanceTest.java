/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.io.IOException;
import java.util.LinkedList;
import java.util.List;

public class AzureBlobStorageJsonlDestinationAcceptanceTest extends
    AzureBlobStorageDestinationAcceptanceTest {

  protected AzureBlobStorageJsonlDestinationAcceptanceTest() {
    super(AzureBlobStorageFormat.JSONL);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"JSONL\"\n"
        + "}");
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws IOException {

    String allSyncedObjects = getAllSyncedObjects(streamName);
    List<JsonNode> jsonRecords = new LinkedList<>();

    allSyncedObjects.lines().forEach(line -> {
      jsonRecords.add(Jsons.deserialize(line).get(JavaBaseConstants.COLUMN_NAME_DATA));
    });
    return jsonRecords;
  }

}
