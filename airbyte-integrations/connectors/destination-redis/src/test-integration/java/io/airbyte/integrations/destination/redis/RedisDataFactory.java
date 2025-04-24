/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;

public class RedisDataFactory {

  private RedisDataFactory() {

  }

  static JsonNode jsonConfig(String host, int port) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", host)
        .put("port", port)
        .put("username", "default")
        .put("password", "pw")
        .put("cache_type", "hash")
        .put("ssl", "false")
        .put("ssl_mode", ImmutableMap.builder()
            .put("mode", "disable")
            .build())
        .build());
  }

}
