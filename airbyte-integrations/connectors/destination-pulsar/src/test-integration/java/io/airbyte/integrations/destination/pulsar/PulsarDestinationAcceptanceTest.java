/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

import org.apache.pulsar.client.api.Consumer;
import org.apache.pulsar.client.api.Message;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.api.SubscriptionType;
import org.testcontainers.containers.PulsarContainer;
import org.testcontainers.utility.DockerImageName;

public class PulsarDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final String TOPIC_NAME = "test.topic";

  private static PulsarContainer PULSAR;

  private final NamingConventionTransformer namingResolver = new StandardNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-pulsar:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("pulsar_brokers", PULSAR.getPulsarBrokerUrl().replaceAll("pulsar://", ""))
        .put("topic_pattern", "{namespace}.{stream}." + TOPIC_NAME)
        .put("use_tls", false)
        .put("access_mode", "Shared")
        .put("sync_producer", true)
        .put("compression_type", "NONE")
        .put("enable_batching", true)
        .put("batching_max_publish_delay", 1)
        .put("batching_max_messages", 1000)
        .put("producer_name", "test-producer")
        .put("block_if_queue_full", true)
        .put("auto_update_partitions", true)
        .put("auto_update_partitions_interval", 60)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("pulsar_brokers", PULSAR.getPulsarBrokerUrl())
        .put("topic_pattern", "{namespace}.{stream}." + TOPIC_NAME)
        .put("use_tls", false)
        .put("sync_producer", true)
        .put("access_mode", "Shared")
        .put("producer_name", "test-producer")
        .put("compression_type", "NONE")
        .put("block_if_queue_full", true)
        .put("auto_update_partitions", true)
        .build());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    return "";
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace) throws PulsarClientException {
    return retrieveRecords(testEnv, streamName, namespace, null);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) throws PulsarClientException {
    final PulsarClient client = PulsarClient.builder()
      .serviceUrl(PULSAR.getPulsarBrokerUrl())
      .build();
    final String topic = namingResolver.getIdentifier(namespace + "." + streamName + "." + TOPIC_NAME);
    final Consumer<JsonNode> consumer = client.newConsumer(Schema.JSON(JsonNode.class))
      .topic(topic)
      .subscriptionName("test-subscription")
      .enableRetry(true)
      .subscriptionType(SubscriptionType.Exclusive)
      .subscribe();

    final List<JsonNode> records = new ArrayList<>();
    consumer.seek(Instant.now().minus(Duration.ofHours(1)).toEpochMilli());

    while(!consumer.hasReachedEndOfTopic()) {
      Message<JsonNode> msg = consumer.receive();
      consumer.acknowledge(msg);
      records.add(msg.getValue());
    }
    consumer.close();
    return records;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    PULSAR = new PulsarContainer(DockerImageName.parse("apachepulsar/pulsar:2.8.1"));
    PULSAR.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    PULSAR.close();
  }

}
