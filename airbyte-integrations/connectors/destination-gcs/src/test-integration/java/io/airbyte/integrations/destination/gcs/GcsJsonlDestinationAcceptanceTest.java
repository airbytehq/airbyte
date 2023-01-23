/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class GcsJsonlDestinationAcceptanceTest extends GcsDestinationAcceptanceTest {

  public GcsJsonlDestinationAcceptanceTest() {
    super(S3Format.JSONL);
  }

  @Override
  public ProtocolVersion getProtocolVersion() {
    return ProtocolVersion.V1;
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.jsonNode(Map.of(
        "format_type", outputFormat,
        "compression", Jsons.jsonNode(Map.of("compression_type", "No Compression"))));
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws IOException {
    final List<S3ObjectSummary> objectSummaries = getAllSyncedObjects(streamName, namespace);
    final List<JsonNode> jsonRecords = new LinkedList<>();

    for (final S3ObjectSummary objectSummary : objectSummaries) {
      final S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
      try (final BufferedReader reader = getReader(object)) {
        String line;
        while ((line = reader.readLine()) != null) {
          jsonRecords.add(Jsons.deserialize(line).get(JavaBaseConstants.COLUMN_NAME_DATA));
        }
      }
    }

    return jsonRecords;
  }

  protected BufferedReader getReader(final S3Object s3Object) throws IOException {
    return new BufferedReader(new InputStreamReader(s3Object.getObjectContent(), StandardCharsets.UTF_8));
  }

}
