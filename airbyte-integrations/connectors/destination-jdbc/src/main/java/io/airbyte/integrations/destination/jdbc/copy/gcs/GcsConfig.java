package io.airbyte.integrations.destination.jdbc.copy.gcs;

import com.fasterxml.jackson.databind.JsonNode;

public class GcsConfig {
    private final String projectId;
    private final String bucketName;
    private final String credentialsJson;

    public GcsConfig(String projectId, String bucketName, String credentialsJson) {
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

    public static GcsConfig getGcsConfig(JsonNode config) {
        return new GcsConfig(
                config.get("project_id").asText(),
                config.get("bucket_name").asText(),
                config.get("credentials_json").asText());
    }
}
