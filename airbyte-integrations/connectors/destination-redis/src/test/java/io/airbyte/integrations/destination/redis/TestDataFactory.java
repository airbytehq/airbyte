/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;

class TestDataFactory {

  private TestDataFactory() {

  }

  static RedisConfig redisConfig(String host, int port) {
    return new RedisConfig(host, port, "default", "pw");
  }

  static JsonNode jsonConfig(String host, int port) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", host)
        .put("port", port)
        .put("username", "default")
        .put("password", "pw")
        .build());
  }

}
