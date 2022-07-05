/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class CassandraConfigTest {

  private CassandraConfig cassandraConfig;

  @BeforeEach
  void setup() {
    var jsonNode = TestDataFactory.createJsonConfig(
        "usr",
        "pw",
        "127.0.0.1",
        9042);
    this.cassandraConfig = new CassandraConfig(jsonNode);
  }

  @Test
  void testConfig() {

    assertThat(cassandraConfig)
        .hasFieldOrPropertyWithValue("keyspace", "default_keyspace")
        .hasFieldOrPropertyWithValue("username", "usr")
        .hasFieldOrPropertyWithValue("password", "pw")
        .hasFieldOrPropertyWithValue("address", "127.0.0.1")
        .hasFieldOrPropertyWithValue("port", 9042)
        .hasFieldOrPropertyWithValue("datacenter", "datacenter1")
        .hasFieldOrPropertyWithValue("replication", 1);

  }

}
