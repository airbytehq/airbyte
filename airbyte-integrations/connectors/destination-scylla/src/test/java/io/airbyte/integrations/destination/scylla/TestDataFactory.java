/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;

class TestDataFactory {

  static JsonNode jsonConfig(String address, int port) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("keyspace", "default_keyspace")
        .put("username", "usr")
        .put("password", "pw")
        .put("address", address)
        .put("port", port)
        .put("replication", 2)
        .build());
  }

  static ScyllaConfig scyllaConfig(String address, int port) {
    return new ScyllaConfig(
        "default_keyspace",
        "usr",
        "pw",
        address,
        port,
        2);
  }

}
