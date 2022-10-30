package io.airbyte.integrations.source.dynamodb;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.commons.json.Jsons;
import java.net.URI;
import java.util.Map;
import org.junit.jupiter.api.Test;
import software.amazon.awssdk.regions.Region;

class DynamodbConfigTest {

    @Test
    void testDynamodbConfig() {

        var jsonConfig = Jsons.jsonNode(Map.of(
            "dynamodb_endpoint", "http://localhost:8080",
            "dynamodb_region", "us-east-1",
            "access_key_id", "A012345678910EXAMPLE",
            "secret_access_key", "a012345678910ABCDEFGH/AbCdEfGhLEKEY"
        ));

        var dynamodbConfig = DynamodbConfig.initConfigFromJson(jsonConfig);

        assertThat(dynamodbConfig)
            .hasFieldOrPropertyWithValue("endpoint", URI.create("http://localhost:8080"))
            .hasFieldOrPropertyWithValue("region", Region.of("us-east-1"))
            .hasFieldOrPropertyWithValue("accessKey", "A012345678910EXAMPLE")
            .hasFieldOrPropertyWithValue("secretKey", "a012345678910ABCDEFGH/AbCdEfGhLEKEY");

    }

}
