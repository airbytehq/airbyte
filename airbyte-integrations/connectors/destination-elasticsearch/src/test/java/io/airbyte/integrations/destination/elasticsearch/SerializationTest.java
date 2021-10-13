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

    String host = "localhost";
    int port = 123;
    String indexPrefix = "data";
    String apiKeyId = "foo";
    String apiKeySecret = "bar";
    boolean ssl = false;

    node
        .put("host", host)
        .put("port", port)
        .put("indexPrefix", indexPrefix)
        .put("apiKeyId", apiKeyId)
        .put("apiKeySecret", apiKeySecret)
        .put("ssl", ssl);

    ConnectorConfiguration config = mapper.convertValue(node, ConnectorConfiguration.class);
    Assertions.assertEquals(host, config.getHost());
    Assertions.assertEquals(port, config.getPort());
    Assertions.assertEquals(indexPrefix, config.getIndexPrefix());
    Assertions.assertEquals(apiKeyId, config.getApiKeyId());
    Assertions.assertEquals(apiKeySecret, config.getApiKeySecret());
    Assertions.assertEquals(ssl, config.isSsl());
  }

}
