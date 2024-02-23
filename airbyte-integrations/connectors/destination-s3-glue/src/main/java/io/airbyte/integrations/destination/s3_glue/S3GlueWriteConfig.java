/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.destination.s3.WriteConfig;
import io.airbyte.protocol.models.v0.DestinationSyncMode;

public class S3GlueWriteConfig extends WriteConfig {

  private final JsonNode jsonSchema;

  private final String location;

  public S3GlueWriteConfig(String namespace,
                           String streamName,
                           String outputBucketPath,
                           String pathFormat,
                           String fullOutputPath,
                           DestinationSyncMode syncMode,
                           JsonNode jsonSchema,
                           String location) {
    super(namespace, streamName, outputBucketPath, pathFormat, fullOutputPath, syncMode);
    this.jsonSchema = jsonSchema;
    this.location = location;
  }

  public JsonNode getJsonSchema() {
    return jsonSchema;
  }

  public String getLocation() {
    return location;
  }

}
