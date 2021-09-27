/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import java.nio.file.Files;
import java.nio.file.Paths;
import org.junit.jupiter.api.Test;

class SnowflakeDestinationTest {

  @Test
  void testCheckFailsWithInvalidPermissions() throws Exception {
    // TODO(sherifnada) this test case is assumes config.json does not have permission to access the
    // schema
    // this connector should be updated with multiple credentials, each with a clear purpose (valid,
    // invalid: insufficient permissions, invalid: wrong password, etc..)
    JsonNode credentialsJsonString = Jsons.deserialize(new String(Files.readAllBytes(Paths.get("secrets/config.json"))));
    AirbyteConnectionStatus check = new SnowflakeDestination().check(credentialsJsonString);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, check.getStatus());
  }

}
