package io.airbyte.cdk.integrations.base.config;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.micronaut.context.annotation.ConfigurationProperties;

@ConfigurationProperties("airbyte.connector.state")
public class AirbyteConnectorState {

    String configured;

    public JsonNode toJson() {
        return Jsons.jsonNode(this);
    }
}
