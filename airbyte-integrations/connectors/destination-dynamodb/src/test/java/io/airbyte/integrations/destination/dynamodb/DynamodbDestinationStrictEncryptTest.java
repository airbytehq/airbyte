/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.junit.jupiter.api.Test;

public class DynamodbDestinationStrictEncryptTest {

  private static final String NON_SECURE_URL_ERR_MSG = "Server Endpoint requires HTTPS";

  /**
   * Test that checks if user is using a connection that is HTTPS only
   */
  @Test
  public void checksCustomEndpointIsHttpsOnly() {
    final DynamodbDestination destinationWithHttpsOnlyEndpoint = new DynamodbDestinationStrictEncrypt();
    final AirbyteConnectionStatus status = destinationWithHttpsOnlyEndpoint.check(getUnsecureConfig());
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertEquals(NON_SECURE_URL_ERR_MSG, status.getMessage());
  }

  protected JsonNode getUnsecureConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("dynamodb_endpoint", "http://testurl.com:9000")
        .put("dynamodb_table_name_prefix", "integration-test")
        .put("dynamodb_region", "us-east-2")
        .put("access_key_id", "dummy_access_key_id")
        .put("secret_access_key", "dummy_secret_access_key")
        .build());
  }

}
