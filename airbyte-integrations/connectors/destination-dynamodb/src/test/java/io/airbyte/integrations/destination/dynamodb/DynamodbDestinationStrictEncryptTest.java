/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import static io.airbyte.integrations.destination.dynamodb.DynamodbDestinationStrictEncrypt.NON_SECURE_URL_ERR_MSG;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

public class DynamodbDestinationStrictEncryptTest {

  protected static final Path secretFilePath = Path.of("secrets/config.json");

  /**
   * Test that check passes if user is using HTTPS connection
   */
  @Test
  public void checkPassCustomEndpointIsHttpsOnly() {
    final DynamodbDestination destinationWithHttpsOnlyEndpoint = new DynamodbDestinationStrictEncrypt();
    final AirbyteConnectionStatus status = destinationWithHttpsOnlyEndpoint.check(getBaseConfigJson());
    assertEquals(Status.SUCCEEDED, status.getStatus());
  }

  /**
   * Test that check fails if user is using a non-secure (http) connection
   */
  @Test
  public void checkFailCustomEndpointIsHttpsOnly() {
    final DynamodbDestination destinationWithHttpsOnlyEndpoint = new DynamodbDestinationStrictEncrypt();
    final AirbyteConnectionStatus status = destinationWithHttpsOnlyEndpoint.check(getUnsecureConfig());
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertEquals(NON_SECURE_URL_ERR_MSG, status.getMessage());
  }

  protected JsonNode getBaseConfigJson() {
    if (!Files.exists(secretFilePath)) {
      throw new IllegalStateException("Secret config file doesn't exist. Get a valid secret (for airbyter: "
          + "get secret from GSM) and put to ../destination-dynamodb/secrets/secret.json file");
    }
    return Jsons.deserialize(IOs.readFile(secretFilePath));
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
