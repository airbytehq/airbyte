/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.time.Instant;
import java.util.List;

public class TestDataFactory {

  private TestDataFactory() {

  }

  static CassandraConfig createCassandraConfig(String username, String password, String address, int port) {
    return new CassandraConfig(
        "default_keyspace",
        username,
        password,
        address,
        port,
        "datacenter1",
        1);
  }

  static JsonNode createJsonConfig(String username, String password, String address, int port) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("keyspace", "default_keyspace")
        .put("username", username)
        .put("password", password)
        .put("address", address)
        .put("port", port)
        .put("datacenter", "datacenter1")
        .put("replication", 1)
        .build());
  }

  static AirbyteMessage createAirbyteMessage(AirbyteMessage.Type type,
                                             String streamName,
                                             String namespace,
                                             JsonNode data) {
    return new AirbyteMessage()
        .withType(type)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withNamespace(namespace)
            .withData(data)
            .withEmittedAt(Instant.now().toEpochMilli()));
  }

  static AirbyteStream createAirbyteStream(String name, String namespace) {
    return new AirbyteStream()
        .withName(name)
        .withNamespace(namespace);
  }

  static ConfiguredAirbyteStream createConfiguredAirbyteStream(DestinationSyncMode syncMode, AirbyteStream stream) {
    return new ConfiguredAirbyteStream()
        .withDestinationSyncMode(syncMode)
        .withStream(stream);
  }

  static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog(ConfiguredAirbyteStream... configuredStreams) {
    return new ConfiguredAirbyteCatalog().withStreams(List.of(configuredStreams));
  }

}
