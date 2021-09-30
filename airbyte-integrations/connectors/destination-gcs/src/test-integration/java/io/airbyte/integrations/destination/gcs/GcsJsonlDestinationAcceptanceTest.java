/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.S3Format;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.LinkedList;
import java.util.List;

public class GcsJsonlDestinationAcceptanceTest extends GcsDestinationAcceptanceTest {

  protected GcsJsonlDestinationAcceptanceTest() {
    super(S3Format.JSONL);
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
    List<S3ObjectSummary> objectSummaries = getAllSyncedObjects(streamName, namespace);
    List<JsonNode> jsonRecords = new LinkedList<>();

    for (S3ObjectSummary objectSummary : objectSummaries) {
      S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
      try (BufferedReader reader = new BufferedReader(new InputStreamReader(object.getObjectContent(), StandardCharsets.UTF_8))) {
        String line;
        while ((line = reader.readLine()) != null) {
          jsonRecords.add(Jsons.deserialize(line).get(JavaBaseConstants.COLUMN_NAME_DATA));
        }
      }
    }

    return jsonRecords;
  }

}
