/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import static io.airbyte.db.mongodb.MongoUtils.AIRBYTE_SUFFIX;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.mongodb.MongoUtils;
import java.util.List;
import org.junit.jupiter.api.Test;

class MongoUtilsTest {

  @Test
  void testTransformToStringIfMarked() {
    final List<String> columnNames = List.of("_id", "createdAt", "connectedWallets", "connectedAccounts_aibyte_transform");
    final String fieldName = "connectedAccounts";
    final JsonNode node = Jsons.deserialize(
        "{\"_id\":\"12345678as\",\"createdAt\":\"2022-11-11 12:13:14\",\"connectedWallets\":\"wallet1\"," +
            "\"connectedAccounts\":" +
            "{\"google\":{\"provider\":\"google\",\"refreshToken\":\"test-rfrsh-google-token-1\",\"accessToken\":\"test-access-google-token-1\",\"expiresAt\":\"2020-09-01T21:07:00Z\",\"createdAt\":\"2020-09-01T20:07:01Z\"},"
            +
            "\"figma\":{\"provider\":\"figma\",\"refreshToken\":\"test-rfrsh-figma-token-1\",\"accessToken\":\"test-access-figma-token-1\",\"expiresAt\":\"2020-12-13T22:08:03Z\",\"createdAt\":\"2020-09-14T22:08:03Z\",\"figmaInfo\":{\"teamID\":\"501087711831561793\"}},"
            +
            "\"slack\":{\"provider\":\"slack\",\"accessToken\":\"test-access-slack-token-1\",\"createdAt\":\"2020-09-01T20:15:07Z\",\"slackInfo\":{\"userID\":\"UM5AD2YCE\",\"teamID\":\"T2VGY5GH5\"}}}}");
    assertTrue(node.get(fieldName).isObject());

    MongoUtils.transformToStringIfMarked((ObjectNode) node, columnNames, fieldName);

    assertNull(node.get(fieldName));
    assertNotNull(node.get(fieldName + AIRBYTE_SUFFIX));
    assertTrue(node.get(fieldName + AIRBYTE_SUFFIX).isTextual());

  }

}
