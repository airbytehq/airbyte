/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.redpanda.RedpandaContainer;

class RedpandaOperationsTest {

  private static final String TEST_TOPIC = "test_topic";

  private RedpandaOperations redpandaOperations;

  private RedpandaConsumer<String, JsonNode> redpandaConsumer;

  private RedpandaContainer redpandaContainer;

  @BeforeEach
  void setup() {
    this.redpandaContainer = RedpandaContainerFactory.createRedpandaContainer();
    this.redpandaContainer.start();
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
        .put("", false)
        .build());
    this.redpandaOperations = new RedpandaOperations(RedpandaConfig.createConfig(jsonConfig));
    this.redpandaConsumer = RedpandaConsumerFactory.getInstance(redpandaContainer.getBootstrapServers(), TEST_TOPIC);
  }

  @AfterEach
  void shutdown() {
    this.redpandaOperations.close();
    this.redpandaConsumer.close();
    this.redpandaContainer.stop();
    this.redpandaContainer.close();
  }

  @Test
  void testPutRecord() {

    redpandaOperations.putRecord(TEST_TOPIC, UUID.randomUUID().toString(), Jsons.jsonNode(Map.of("attr_1", "data1")), e -> {});
    redpandaOperations.putRecord(TEST_TOPIC, UUID.randomUUID().toString(), Jsons.jsonNode(Map.of("attr_1", "data2")), e -> {});
    redpandaOperations.flush();

    List<JsonNode> records = new ArrayList<>();
    redpandaConsumer.subscribe(Collections.singletonList(TEST_TOPIC));
    redpandaConsumer.poll(Duration.ofSeconds(5)).iterator().forEachRemaining(r -> records.add(r.value()));

    assertThat(records)
        .hasSize(2);
  }

  @Test
  void testCreateTopic() {

    var topicInfo = new RedpandaOperations.TopicInfo(TEST_TOPIC, Optional.of(1), Optional.of((short) 1));
    redpandaOperations.createTopic(Set.of(topicInfo));

    Set<String> topics = redpandaOperations.listTopics();

    assertThat(topics).anyMatch(topic -> topic.equals(TEST_TOPIC));
  }

  @Test
  void testDeleteTopic() {

    // given
    var topicInfo = new RedpandaOperations.TopicInfo(TEST_TOPIC, Optional.of(1), Optional.of((short) 1));
    redpandaOperations.createTopic(Set.of(topicInfo));

    // when
    redpandaOperations.deleteTopic(Set.of(TEST_TOPIC));

    // then
    Set<String> topics = redpandaOperations.listTopics();

    assertThat(topics).isEmpty();

  }

  @Test
  void testPutRecordBlocking() {

    redpandaOperations.putRecordBlocking(TEST_TOPIC, UUID.randomUUID().toString(), Jsons.jsonNode(Map.of("attr_1", "data1")));
    redpandaOperations.putRecordBlocking(TEST_TOPIC, UUID.randomUUID().toString(), Jsons.jsonNode(Map.of("attr_1", "data2")));
    redpandaOperations.flush();

    List<JsonNode> records = new ArrayList<>();
    redpandaConsumer.subscribe(Collections.singletonList(TEST_TOPIC));
    redpandaConsumer.poll(Duration.ofSeconds(5)).iterator().forEachRemaining(r -> records.add(r.value()));

    assertThat(records)
        .hasSize(2);

  }

}
