/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ScyllaConfigTest {

  private ScyllaConfig scyllaConfig;

  @BeforeEach
  void setup() {
    var jsonNode = TestDataFactory.jsonConfig("127.0.0.1", 9042);
    this.scyllaConfig = new ScyllaConfig(jsonNode);
  }

  @Test
  void testConfig() {

    assertThat(scyllaConfig)
        .hasFieldOrPropertyWithValue("keyspace", "default_keyspace")
        .hasFieldOrPropertyWithValue("username", "usr")
        .hasFieldOrPropertyWithValue("password", "pw")
        .hasFieldOrPropertyWithValue("address", "127.0.0.1")
        .hasFieldOrPropertyWithValue("port", 9042)
        .hasFieldOrPropertyWithValue("replication", 2);

  }

}
