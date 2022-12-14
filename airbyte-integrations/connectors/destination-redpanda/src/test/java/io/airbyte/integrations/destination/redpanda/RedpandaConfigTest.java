/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.commons.json.Jsons;
import java.util.Comparator;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class RedpandaConfigTest {

  @Test
  void testRedpandaConfig() {

    var jsonConfig = Jsons.jsonNode(Map.of(
        "bootstrap_servers", "host1:port1,host2:port2",
        "buffer_memory", 33554432L,
        "compression_type", "none",
        "retries", 5,
        "batch_size", 16384,
        "topic_num_partitions", 1,
        "topic_replication_factor", 1,
        "socket_connection_setup_timeout_ms", 10000,
        "socket_connection_setup_timeout_max_ms", 30000));

    var redpandaConfig = RedpandaConfig.createConfig(jsonConfig);

    assertThat(redpandaConfig)
        .usingComparatorForFields(new OptionalComparator(), "topicNumPartitions", "topicReplicationFactor")
        .hasFieldOrPropertyWithValue("bootstrapServers", "host1:port1,host2:port2")
        .hasFieldOrPropertyWithValue("bufferMemory", 33554432L)
        .hasFieldOrPropertyWithValue("compressionType", "none")
        .hasFieldOrPropertyWithValue("retries", 5)
        .hasFieldOrPropertyWithValue("batchSize", 16384)
        .hasFieldOrPropertyWithValue("topicNumPartitions", Optional.of(1))
        .hasFieldOrPropertyWithValue("topicReplicationFactor", Optional.of((short) 1))
        .hasFieldOrPropertyWithValue("socketConnectionSetupTimeoutMs", 10000)
        .hasFieldOrPropertyWithValue("socketConnectionSetupTimeoutMaxMs", 30000);

  }

  private static class OptionalComparator implements Comparator<Optional<Integer>> {

    @Override
    public int compare(Optional<Integer> o1, Optional<Integer> o2) {
      return Integer.compare(o1.get(), o2.get());
    }

  }

}
