/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import org.apache.pulsar.client.api.Producer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.testcontainers.containers.PulsarContainer;
import org.testcontainers.utility.DockerImageName;

@DisplayName("PulsarRecordConsumer")
public class PulsarRecordConsumerTest {

  private static final String TOPIC_NAME = "test.topic";
  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";

  private static final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createConfiguredAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaPrimitive.NUMBER),
          Field.of("name", JsonSchemaPrimitive.STRING))));

  private static final StandardNameTransformer NAMING_RESOLVER = new StandardNameTransformer();

  private static PulsarContainer PULSAR;

  @ParameterizedTest
  @ArgumentsSource(TopicMapArgumentsProvider.class)
  @SuppressWarnings("unchecked")
  public void testBuildProducerMap(final String topicPattern, final String expectedTopic) {
    final PulsarDestinationConfig config = PulsarDestinationConfig
      .getPulsarDestinationConfig(getConfig(PULSAR.getPulsarBrokerUrl().replaceAll("pulsar://", ""), topicPattern));
    final PulsarRecordConsumer recordConsumer = new PulsarRecordConsumer(config, CATALOG, mock(Consumer.class), NAMING_RESOLVER);

    final Map<AirbyteStreamNameNamespacePair, Producer<JsonNode>> producerMap = recordConsumer.buildProducerMap();
    assertEquals(1, producerMap.size());

    final AirbyteStreamNameNamespacePair streamNameNamespacePair = new AirbyteStreamNameNamespacePair(STREAM_NAME, SCHEMA_NAME);
    assertEquals(expectedTopic, producerMap.get(streamNameNamespacePair).getTopic());
  }

  @Test
  @SuppressWarnings("unchecked")
  void testCannotConnectToBrokers() throws Exception {
    final PulsarDestinationConfig config = PulsarDestinationConfig.getPulsarDestinationConfig(getConfig("localhost:33233", TOPIC_NAME));
    final PulsarRecordConsumer consumer = new PulsarRecordConsumer(config, CATALOG, mock(Consumer.class), NAMING_RESOLVER);
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    assertThrows(RuntimeException.class, consumer::start);

    expectedRecords.forEach(m -> assertThrows(RuntimeException.class, () -> consumer.accept(m)));

    consumer.accept(new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(SCHEMA_NAME + "." + STREAM_NAME, 0)))));
    consumer.close();
  }

  private JsonNode getConfig(final String pulsarBrokers, final String topic) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("pulsar_brokers", pulsarBrokers)
        .put("topic_pattern", topic)
        .put("use_tls", false)
        .put("access_mode", "Shared")
        .put("sync_producer", true)
        .put("compression_type", "NONE")
        .put("enable_batching", true)
        .put("batching_max_publish_delay", 1)
        .put("batching_max_messages", 1000)
        .put("enable_chunking", false)
        .put("producer_name", "test-producer")
        .put("block_if_queue_full", true)
        .put("auto_update_partitions", true)
        .put("auto_update_partitions_interval", 60)
        .build());
  }

  private List<AirbyteMessage> getNRecords(final int n) {
    return IntStream.range(0, n)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(STREAM_NAME)
                .withNamespace(SCHEMA_NAME)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
        .collect(Collectors.toList());

  }

  public static class TopicMapArgumentsProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) {
      return Stream.of(
          Arguments.of(TOPIC_NAME, "test_topic"),
          Arguments.of("test-topic", "test_topic"),
          Arguments.of("{namespace}", SCHEMA_NAME),
          Arguments.of("{stream}", STREAM_NAME),
          Arguments.of("{namespace}.{stream}." + TOPIC_NAME, "public_id_and_name_test_topic"),
          Arguments.of("{namespace}-{stream}-" + TOPIC_NAME, "public_id_and_name_test_topic"),
          Arguments.of("topic with spaces", "topic_with_spaces"));
    }

  }

  @BeforeEach
  void setup() {
    PULSAR = new PulsarContainer(DockerImageName.parse("apachepulsar/pulsar:2.8.1"));
    PULSAR.start();
  }

  @AfterEach
  void tearDown() {
    PULSAR.close();
  }

}
