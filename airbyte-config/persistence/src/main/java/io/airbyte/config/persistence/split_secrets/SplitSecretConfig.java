package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;

import java.util.Map;

public class SplitSecretConfig {
    private final JsonNode partialConfig;
    private final Map<String, String> secretIdToPayload;

    public SplitSecretConfig(final JsonNode partialConfig, final Map<String, String> secretIdToPayload) {
        this.partialConfig = partialConfig;
        this.secretIdToPayload = secretIdToPayload;
    }

    public JsonNode getPartialConfig() {
        return partialConfig;
    }

    public Map<String, String> getSecretIdToPayload() {
        return secretIdToPayload;
    }
}
