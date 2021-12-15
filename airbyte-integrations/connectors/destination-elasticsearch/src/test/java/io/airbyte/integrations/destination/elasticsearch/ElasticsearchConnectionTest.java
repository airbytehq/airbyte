/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import java.util.Base64;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class ElasticsearchConnectionTest {

  String endpoint = "https:qwerty:123";

  @Test
  public void testDefaultHeadersAuthNone() {
    var config = new ConnectorConfiguration();
    config.setEndpoint(endpoint);
    config.getAuthenticationMethod().setMethod(ElasticsearchAuthenticationMethod.none);
    var connection = new ElasticsearchConnection(config);
    var headers = connection.configureHeaders(config);
    Assertions.assertEquals(0, headers.length);
  }

  @Test
  public void testDefaultHeadersAuthBasic() {
    var config = new ConnectorConfiguration();
    config.setEndpoint(endpoint);
    config.getAuthenticationMethod().setUsername("user");
    config.getAuthenticationMethod().setPassword("password");
    config.getAuthenticationMethod().setMethod(ElasticsearchAuthenticationMethod.basic);
    var connection = new ElasticsearchConnection(config);
    var headers = connection.configureHeaders(config);
    Assertions.assertEquals(1, headers.length);

    var headerValues = headers[0].getValue().split(" ");
    Assertions.assertEquals("Basic", headerValues[0]);
    var decoded = Base64.getDecoder().decode(headerValues[1]);
    Assertions.assertTrue("user:password".contentEquals(new String(decoded)));
  }

  @Test
  public void testDefaultHeadersAuthSecret() {
    var config = new ConnectorConfiguration();
    config.setEndpoint(endpoint);
    config.getAuthenticationMethod().setApiKeyId("id");
    config.getAuthenticationMethod().setApiKeySecret("secret");
    config.getAuthenticationMethod().setMethod(ElasticsearchAuthenticationMethod.secret);
    var connection = new ElasticsearchConnection(config);
    var headers = connection.configureHeaders(config);
    Assertions.assertEquals(1, headers.length);

    var headerValues = headers[0].getValue().split(" ");
    Assertions.assertEquals("ApiKey", headerValues[0]);
    var decoded = Base64.getDecoder().decode(headerValues[1]);
    Assertions.assertTrue("id:secret".contentEquals(new String(decoded)));
  }

}
