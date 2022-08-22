/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectReader;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Streams;
import com.google.common.net.InetAddresses;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.io.IOException;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.pulsar.client.api.Consumer;
import org.apache.pulsar.client.api.Message;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.api.SubscriptionInitialPosition;
import org.apache.pulsar.client.api.SubscriptionType;
import org.apache.pulsar.client.api.schema.GenericRecord;
import org.testcontainers.containers.PulsarContainer;
import org.testcontainers.utility.DockerImageName;

public class PulsarDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final String TOPIC_NAME = "test.topic";
  private static final ObjectReader READER = new ObjectMapper().reader();

  private static PulsarContainer PULSAR;

  private final NamingConventionTransformer namingResolver = new StandardNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-pulsar:dev";
  }

  @Override
  protected JsonNode getConfig() throws UnknownHostException {
    String brokers = Stream.concat(getIpAddresses().stream(), Stream.of("localhost"))
        .map(ip -> ip + ":" + PULSAR.getMappedPort(PulsarContainer.BROKER_PORT))
        .collect(Collectors.joining(","));
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("brokers", brokers)
        .put("use_tls", false)
        .put("topic_type", "persistent")
        .put("topic_tenant", "public")
        .put("topic_namespace", "default")
        .put("topic_pattern", "{namespace}.{stream}." + TOPIC_NAME)
        .put("producer_name", "test-producer-" + UUID.randomUUID())
        .put("producer_sync", true)
        .put("compression_type", "NONE")
        .put("send_timeout_ms", 30000)
        .put("max_pending_messages", 1000)
        .put("max_pending_messages_across_partitions", 50000)
        .put("batching_enabled", false)
        .put("batching_max_messages", 1000)
        .put("batching_max_publish_delay", 1)
        .put("block_if_queue_full", true)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("brokers", PULSAR.getHost() + ":" + PULSAR.getMappedPort(PulsarContainer.BROKER_PORT))
        .put("use_tls", false)
        .put("topic_pattern", "{namespace}.{stream}." + TOPIC_NAME)
        .put("producer_sync", true)
        .put("producer_name", "test-producer")
        .put("compression_type", "NONE")
        .put("send_timeout_ms", 30000)
        .put("max_pending_messages", 1000)
        .put("max_pending_messages_across_partitions", 50000)
        .put("block_if_queue_full", true)
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
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws IOException {
    return retrieveRecords(testEnv, streamName, namespace, null);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws IOException {
    final PulsarClient client = PulsarClient.builder()
        .serviceUrl(PULSAR.getPulsarBrokerUrl())
        .build();
    final String topic = namingResolver.getIdentifier(namespace + "." + streamName + "." + TOPIC_NAME);
    final Consumer<GenericRecord> consumer = client.newConsumer(Schema.AUTO_CONSUME())
        .topic(topic)
        .subscriptionName("test-subscription-" + UUID.randomUUID())
        .enableRetry(true)
        .subscriptionType(SubscriptionType.Exclusive)
        .subscriptionInitialPosition(SubscriptionInitialPosition.Earliest)
        .subscribe();

    final List<JsonNode> records = new ArrayList<>();
    while (!consumer.hasReachedEndOfTopic()) {
      Message<GenericRecord> message = consumer.receive(5, TimeUnit.SECONDS);
      if (message == null) {
        break;
      }
      records.add(READER.readTree(Base64.getDecoder().decode(message.getValue().getField(PulsarDestination.COLUMN_NAME_DATA).toString())));
      Exceptions.swallow(() -> consumer.acknowledge(message));
    }
    consumer.unsubscribe();
    consumer.close();
    client.close();

    return records;
  }

  @SuppressWarnings("UnstableApiUsage")
  private List<String> getIpAddresses() throws UnknownHostException {
    try {
      return Streams.stream(NetworkInterface.getNetworkInterfaces().asIterator())
          .flatMap(ni -> Streams.stream(ni.getInetAddresses().asIterator()))
          .map(InetAddress::getHostAddress)
          .filter(InetAddresses::isUriInetAddress)
          .collect(Collectors.toList());
    } catch (SocketException e) {
      return Collections.singletonList(InetAddress.getLocalHost().getHostAddress());
    }
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
