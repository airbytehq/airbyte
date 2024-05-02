/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.commons.json.Jsons;
import java.net.URI;
import java.util.Collections;
import java.util.Map;
import org.junit.jupiter.api.Test;
import software.amazon.awssdk.regions.Region;

class DynamodbConfigTest {

  @Test
  void testUserBasedDynamodbConfig() {

    var jsonConfig = Jsons.jsonNode(Map.of(
        "endpoint", "http://localhost:8080",
        "region", "us-east-1",
        "credentials", Map.of("auth_type", "User", "access_key_id", "A012345678910EXAMPLE",
            "secret_access_key", "a012345678910ABCDEFGH/AbCdEfGhLEKEY")));

    var dynamodbConfig = DynamodbConfig.createDynamodbConfig(jsonConfig);

    assertThat(dynamodbConfig)
        .hasFieldOrPropertyWithValue("endpoint", URI.create("http://localhost:8080"))
        .hasFieldOrPropertyWithValue("region", Region.of("us-east-1"))
        .hasFieldOrPropertyWithValue("accessKey", "A012345678910EXAMPLE")
        .hasFieldOrPropertyWithValue("secretKey", "a012345678910ABCDEFGH/AbCdEfGhLEKEY")
        .hasFieldOrPropertyWithValue("reservedAttributeNames", Collections.emptyList())
        .hasFieldOrPropertyWithValue("ignoreMissingPermissions", false);

  }

  @Test
  void testRoleBasedDynamodbConfig() {
    var jsonConfig = Jsons.jsonNode(Map.of(
        "endpoint", "http://localhost:8080",
        "region", "us-east-1",
        "credentials", Map.of("auth_type", "Role")));

    var dynamodbConfig = DynamodbConfig.createDynamodbConfig(jsonConfig);

    assertThat(dynamodbConfig)
        .hasFieldOrPropertyWithValue("endpoint", URI.create("http://localhost:8080"))
        .hasFieldOrPropertyWithValue("region", Region.of("us-east-1"));
  }

}
