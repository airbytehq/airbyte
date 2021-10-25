/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class SerializationTest {

  private ObjectMapper mapper = new ObjectMapper();

  @Test
  public void test() {

    ObjectNode node = mapper.createObjectNode();
    ObjectNode authNode = mapper.createObjectNode();

    String endpoint = "http://localhost:123";
    String indexPrefix = "data";
    String apiKeyId = "foo";
    String apiKeySecret = "bar";

    node
        .put("endpoint", endpoint)
        .put("indexPrefix", indexPrefix)
        .set("authenticationMethod", authNode);

    authNode
        .put("apiKeyId", apiKeyId)
        .put("apiKeySecret", apiKeySecret);

    ConnectorConfiguration config = mapper.convertValue(node, ConnectorConfiguration.class);
    Assertions.assertTrue(config.getAuthenticationMethod().isValid());
    Assertions.assertEquals(endpoint, config.getEndpoint());
    Assertions.assertEquals(apiKeyId, config.getAuthenticationMethod().getApiKeyId());
    Assertions.assertEquals(apiKeySecret, config.getAuthenticationMethod().getApiKeySecret());
  }

}
