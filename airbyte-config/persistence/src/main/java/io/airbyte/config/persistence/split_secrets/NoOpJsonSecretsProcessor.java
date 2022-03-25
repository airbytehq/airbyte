package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;

public class NoOpJsonSecretsProcessor implements JsonSecretsProcessor {

  @Override public JsonNode maskSecrets(final JsonNode obj, final JsonNode schema) {
    return obj;
  }

  @Override public JsonNode copySecrets(final JsonNode src, final JsonNode dst, final JsonNode schema) {
    return src;
  }
}
