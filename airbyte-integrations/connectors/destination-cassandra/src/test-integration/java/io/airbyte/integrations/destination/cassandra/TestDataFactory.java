/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
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
        .withNamespace(namespace)
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH));
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
