/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.json.Jsons;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.stream.Collectors;
import org.apache.kafka.clients.admin.Admin;
import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.admin.AdminClientConfig;
import org.apache.kafka.clients.admin.TopicListing;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.redpanda.RedpandaContainer;

public class RedpandaDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedpandaDestinationAcceptanceTest.class);

  private static RedpandaContainer redpandaContainer;

  private RedpandaNameTransformer redpandaNameTransformer;

  private Admin adminClient;

  @BeforeAll
  static void initContainer() {
    redpandaContainer = RedpandaContainerFactory.createRedpandaContainer();
    redpandaContainer.start();
  }

  @AfterAll
  static void stopContainer() {
    redpandaContainer.stop();
    redpandaContainer.close();
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    this.redpandaNameTransformer = new RedpandaNameTransformer();
    this.adminClient = AdminClient.create(Map.of(
        AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, redpandaContainer.getBootstrapServers(),
        AdminClientConfig.RETRIES_CONFIG, 5,
        AdminClientConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MS_CONFIG, 3000,
        AdminClientConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MAX_MS_CONFIG, 30000));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws ExecutionException, InterruptedException {
    final var topics = adminClient.listTopics().listings().get().stream()
        .filter(tl -> !tl.isInternal())
        .map(TopicListing::name)
        .collect(Collectors.toSet());

    adminClient.deleteTopics(topics);
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-redpanda:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
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
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
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
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    final List<JsonNode> records = new ArrayList<>();
    final String bootstrapServers = redpandaContainer.getBootstrapServers();
    final String groupId = redpandaNameTransformer.getIdentifier(namespace + "-" + streamName);
    try (final RedpandaConsumer<String, JsonNode> redpandaConsumer = RedpandaConsumerFactory.getInstance(bootstrapServers, groupId)) {
      final String topicName = redpandaNameTransformer.topicName(namespace, streamName);
      redpandaConsumer.subscribe(Collections.singletonList(topicName));
      redpandaConsumer.poll(Duration.ofSeconds(5)).iterator()
          .forEachRemaining(r -> records.add(r.value().get(JavaBaseConstants.COLUMN_NAME_DATA)));
    }
    return records;
  }

}
