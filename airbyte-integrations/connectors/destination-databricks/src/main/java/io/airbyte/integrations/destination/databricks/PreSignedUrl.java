package io.airbyte.integrations.destination.databricks;

public record PreSignedUrl(String url, long expirationTimeMillis) {

}
