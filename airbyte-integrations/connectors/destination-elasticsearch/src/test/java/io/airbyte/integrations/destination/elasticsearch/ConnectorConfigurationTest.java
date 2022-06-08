/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class ConnectorConfigurationTest {

  private ObjectMapper mapper = new ObjectMapper();

  @Test
  public void testAuthenticationSecret() {

    ObjectNode node = mapper.createObjectNode();
    ObjectNode authNode = mapper.createObjectNode();

    String endpoint = "http://localhost:123";
    String authMethod = ElasticsearchAuthenticationMethod.secret.toString();
    String apiKeyId = "foo";
    String apiKeySecret = "bar";

    node
        .put("endpoint", endpoint)
        .set("authenticationMethod", authNode);

    authNode
        .put("method", authMethod)
        .put("apiKeyId", apiKeyId)
        .put("apiKeySecret", apiKeySecret);

    ConnectorConfiguration config = mapper.convertValue(node, ConnectorConfiguration.class);
    Assertions.assertTrue(config.getAuthenticationMethod().isValid());
    Assertions.assertEquals(endpoint, config.getEndpoint());
    Assertions.assertEquals(authMethod, config.getAuthenticationMethod().getMethod().toString());
    Assertions.assertEquals(apiKeyId, config.getAuthenticationMethod().getApiKeyId());
    Assertions.assertEquals(apiKeySecret, config.getAuthenticationMethod().getApiKeySecret());
  }

  @Test
  public void testAuthenticationBasic() {

    ObjectNode node = mapper.createObjectNode();
    ObjectNode authNode = mapper.createObjectNode();

    String endpoint = "http://localhost:123";
    String authMethod = ElasticsearchAuthenticationMethod.basic.toString();
    String username = "foo";
    String password = "bar";

    node
        .put("endpoint", endpoint)
        .set("authenticationMethod", authNode);

    authNode
        .put("method", authMethod)
        .put("username", username)
        .put("password", password);

    ConnectorConfiguration config = mapper.convertValue(node, ConnectorConfiguration.class);
    Assertions.assertTrue(config.getAuthenticationMethod().isValid());
    Assertions.assertEquals(endpoint, config.getEndpoint());
    Assertions.assertEquals(authMethod, config.getAuthenticationMethod().getMethod().toString());
    Assertions.assertEquals(username, config.getAuthenticationMethod().getUsername());
    Assertions.assertEquals(password, config.getAuthenticationMethod().getPassword());
  }

  @Test
  public void testAuthenticationNone() {

    ObjectNode node = mapper.createObjectNode();
    ObjectNode authNode = mapper.createObjectNode();

    String endpoint = "http://localhost:123";
    String authMethod = ElasticsearchAuthenticationMethod.none.toString();

    node
        .put("endpoint", endpoint)
        .set("authenticationMethod", authNode);

    authNode
        .put("method", authMethod);

    ConnectorConfiguration config = mapper.convertValue(node, ConnectorConfiguration.class);
    Assertions.assertTrue(config.getAuthenticationMethod().isValid());
    Assertions.assertEquals(endpoint, config.getEndpoint());
    Assertions.assertEquals(authMethod, config.getAuthenticationMethod().getMethod().toString());
  }

}
