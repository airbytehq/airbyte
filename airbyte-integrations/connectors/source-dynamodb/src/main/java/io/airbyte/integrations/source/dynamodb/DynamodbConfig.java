package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import java.net.URI;
import software.amazon.awssdk.regions.Region;

public record DynamodbConfig(

    URI endpoint,

    Region region,

    String accessKey,

    String secretKey

) {

    public static DynamodbConfig initConfigFromJson(JsonNode jsonNode) {
        String strend = jsonNode.get("dynamodb_endpoint").asText();
        return new DynamodbConfig(
            strend != null && !strend.isBlank() ? URI.create(strend) : null,
            Region.of(jsonNode.get("dynamodb_region").asText()),
            jsonNode.get("access_key_id").asText(),
            jsonNode.get("secret_access_key").asText()
        );
    }

}
