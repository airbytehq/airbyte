/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import static org.assertj.core.api.Assertions.assertThat;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.redpanda.RedpandaContainer;

class RedpandaDestinationTest {

  private RedpandaContainer redpandaContainer;

  private RedpandaDestination redpandaDestination;

  @BeforeEach
  void setup() {
    this.redpandaDestination = new RedpandaDestination();
    this.redpandaContainer = RedpandaContainerFactory.createRedpandaContainer();
    this.redpandaContainer.start();
  }

  @AfterEach
  void shutdown() {
    this.redpandaContainer.stop();
    this.redpandaContainer.close();
  }

  @Test
  void testCheckWithSuccess() {

    var jsonConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", redpandaContainer.getBootstrapServers())
        .put("compression_type", "none")
        .put("batch_size", 16384)
        .put("buffer_memory", "33554432")
        .put("retries", 1)
        .put("topic_num_partitions", 1)
        .put("topic_replication_factor", 1)
        .put("socket_connection_setup_timeout_ms", 3000)
        .put("socket_connection_setup_timeout_max_ms", 3000)
        .build());

    var status = redpandaDestination.check(jsonConfig);

    assertThat(status.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.SUCCEEDED);

  }

  @Test
  void testCheckWithFailure() {

    var jsonConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", "127.0.0.9")
        .put("compression_type", "none")
        .put("batch_size", 16384)
        .put("buffer_memory", "33554432")
        .put("retries", 1)
        .put("topic_num_partitions", 1)
        .put("topic_replication_factor", 1)
        .put("socket_connection_setup_timeout_ms", 3000)
        .put("socket_connection_setup_timeout_max_ms", 3000)
        .build());

    var status = redpandaDestination.check(jsonConfig);

    assertThat(status.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.FAILED);

  }

}
