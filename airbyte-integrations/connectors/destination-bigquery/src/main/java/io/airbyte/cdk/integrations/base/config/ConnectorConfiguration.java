package io.airbyte.cdk.integrations.base.config;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;

import java.util.Optional;

public interface ConnectorConfiguration {

    Optional<String> getRawNamespace();

    default JsonNode toJson() {
        return Jsons.jsonNode(this);
    }
}
