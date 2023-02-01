/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Sets;
import com.google.common.collect.Streams;
import com.google.common.net.InetAddresses;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.schema.GenericRecord;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.testcontainers.containers.PulsarContainer;
import org.testcontainers.utility.DockerImageName;

@DisplayName("PulsarRecordConsumer")
@ExtendWith(MockitoExtension.class)
public class PulsarRecordConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  private PulsarRecordConsumer consumer;

  @Mock
  private PulsarDestinationConfig config;

  @Mock
  private ConfiguredAirbyteCatalog catalog;

  @Mock
  private PulsarClient pulsarClient;

  private static final StandardNameTransformer NAMING_RESOLVER = new StandardNameTransformer();

  private static PulsarContainer PULSAR;

  @ParameterizedTest
  @ArgumentsSource(TopicMapArgumentsProvider.class)
  @SuppressWarnings("unchecked")
  public void testBuildProducerMap(final ConfiguredAirbyteCatalog catalog,
                                   final String streamName,
                                   final String namespace,
                                   final String topicPattern,
                                   final String expectedTopic)
      throws UnknownHostException {
    String brokers = Stream.concat(getIpAddresses().stream(), Stream.of("localhost"))
        .map(ip -> ip + ":" + PULSAR.getMappedPort(PulsarContainer.BROKER_PORT))
        .collect(Collectors.joining(","));
    final PulsarDestinationConfig config = PulsarDestinationConfig
        .getPulsarDestinationConfig(getConfig(brokers, topicPattern));
    final PulsarClient pulsarClient = PulsarUtils.buildClient(config.getServiceUrl());
    final PulsarRecordConsumer recordConsumer = new PulsarRecordConsumer(config, catalog, pulsarClient, outputRecordCollector, NAMING_RESOLVER);
    final Map<AirbyteStreamNameNamespacePair, Producer<GenericRecord>> producerMap = recordConsumer.buildProducerMap();
    assertEquals(Sets.newHashSet(catalog.getStreams()).size(), producerMap.size());

    final AirbyteStreamNameNamespacePair streamNameNamespacePair = new AirbyteStreamNameNamespacePair(streamName, namespace);
    assertEquals(expectedTopic, producerMap.get(streamNameNamespacePair).getTopic());
  }

  @Test
  @SuppressWarnings("unchecked")
  void testCannotConnectToBrokers() throws Exception {
    final PulsarDestinationConfig config = PulsarDestinationConfig
        .getPulsarDestinationConfig(getConfig(PULSAR.getHost() + ":" + (PULSAR.getMappedPort(PulsarContainer.BROKER_PORT) + 10), "test-topic"));

    final String streamName = "test-stream";
    final String namespace = "test-schema";
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createConfiguredAirbyteStream(
            streamName,
            namespace,
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING))));
    final PulsarClient pulsarClient = PulsarUtils.buildClient(config.getServiceUrl());
    final PulsarRecordConsumer consumer = new PulsarRecordConsumer(config, catalog, pulsarClient, outputRecordCollector, NAMING_RESOLVER);
    final List<AirbyteMessage> expectedRecords = getNRecords(10, streamName, namespace);

    assertThrows(RuntimeException.class, consumer::start);

    expectedRecords.forEach(m -> assertThrows(RuntimeException.class, () -> consumer.accept(m)));

    consumer.accept(new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(namespace + "." + streamName, 0)))));
    consumer.close();
  }

  private JsonNode getConfig(final String brokers, final String topic) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("brokers", brokers)
        .put("use_tls", false)
        .put("topic_type", "non-persistent")
        .put("topic_tenant", "public")
        .put("topic_namespace", "default")
        .put("topic_pattern", topic)
        .put("producer_sync", true)
        .put("compression_type", "NONE")
        .put("send_timeout_ms", 30000)
        .put("max_pending_messages", 1000)
        .put("max_pending_messages_across_partitions", 50000)
        .put("batching_enabled", true)
        .put("batching_max_messages", 1000)
        .put("batching_max_publish_delay", 1)
        .put("block_if_queue_full", true)
        .build());
  }

  private List<AirbyteMessage> getNRecords(final int n, final String streamName, final String namespace) {
    return IntStream.range(0, n)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(streamName)
                .withNamespace(namespace)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
        .collect(Collectors.toList());

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

  public static class TopicMapArgumentsProvider implements ArgumentsProvider {

    private static final String TOPIC_NAME = "test.topic";
    private static final String SCHEMA_NAME1 = "public";
    private static final String STREAM_NAME1 = "id_and_name";
    private static final String SCHEMA_NAME2 = SCHEMA_NAME1 + 2;
    private static final String STREAM_NAME2 = STREAM_NAME1 + 2;

    private final ConfiguredAirbyteStream stream1 = CatalogHelpers.createConfiguredAirbyteStream(
        SCHEMA_NAME1,
        STREAM_NAME1,
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("name", JsonSchemaType.STRING));
    private final ConfiguredAirbyteStream stream2 = CatalogHelpers.createConfiguredAirbyteStream(
        SCHEMA_NAME2,
        STREAM_NAME2,
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("name", JsonSchemaType.STRING));

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) {
      final String prefix = "non-persistent://public/default/";

      final List<ConfiguredAirbyteCatalog> catalogs = new ArrayList<>();
      catalogs.add(new ConfiguredAirbyteCatalog().withStreams(List.of(stream1)));
      catalogs.add(new ConfiguredAirbyteCatalog().withStreams(List.of(stream1, stream1)));
      catalogs.add(new ConfiguredAirbyteCatalog().withStreams(List.of(stream1, stream2)));

      return catalogs.stream()
          .flatMap(catalog -> catalog.getStreams().stream()
              .map(stream -> buildArgs(catalog, stream.getStream(), prefix))
              .flatMap(Collection::stream));
    }

    private List<Arguments> buildArgs(final ConfiguredAirbyteCatalog catalog, final AirbyteStream stream, final String prefix) {
      final String transformedTopic = NAMING_RESOLVER.getIdentifier(TOPIC_NAME);
      final String transformedName = NAMING_RESOLVER.getIdentifier(stream.getName());
      final String transformedNamespace = NAMING_RESOLVER.getIdentifier(stream.getNamespace());

      return ImmutableList.of(
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), TOPIC_NAME, prefix + "test_topic"),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "test-topic", prefix + "test_topic"),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "{namespace}", prefix + transformedNamespace),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "{stream}", prefix + transformedName),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "{namespace}.{stream}." + TOPIC_NAME,
              prefix + transformedNamespace + "_" + transformedName + "_" + transformedTopic),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "{namespace}-{stream}-" + TOPIC_NAME,
              prefix + transformedNamespace + "_" + transformedName + "_" + transformedTopic),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "topic with spaces", prefix + "topic_with_spaces"));
    }

  }

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return consumer;
  }

  @BeforeEach
  void setup() {
    // TODO: Unit tests should not use Testcontainers
    PULSAR = new PulsarContainer(DockerImageName.parse("apachepulsar/pulsar:2.8.1"));
    PULSAR.start();
    consumer = new PulsarRecordConsumer(config, catalog, pulsarClient, outputRecordCollector, NAMING_RESOLVER);
  }

  @AfterEach
  void tearDown() {
    PULSAR.close();
  }

}
