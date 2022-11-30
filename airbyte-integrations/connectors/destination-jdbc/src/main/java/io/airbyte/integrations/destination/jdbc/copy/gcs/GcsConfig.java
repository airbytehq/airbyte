/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.gcs;

import com.fasterxml.jackson.databind.JsonNode;

public class GcsConfig {

  private final String projectId;
  private final String bucketName;
  private final String credentialsJson;

  public GcsConfig(final String projectId, final String bucketName, final String credentialsJson) {
    this.projectId = projectId;
    this.bucketName = bucketName;
    this.credentialsJson = credentialsJson;
  }

  public String getProjectId() {
    return projectId;
  }

  public String getBucketName() {
    return bucketName;
  }

  public String getCredentialsJson() {
    return credentialsJson;
  }

  public static GcsConfig getGcsConfig(final JsonNode config) {
    return new GcsConfig(
        config.get("loading_method").get("project_id").asText(),
        config.get("loading_method").get("bucket_name").asText(),
        config.get("loading_method").get("credentials_json").asText());
  }

}
