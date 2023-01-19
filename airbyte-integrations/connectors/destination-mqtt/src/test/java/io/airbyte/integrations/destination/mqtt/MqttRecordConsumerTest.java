/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mqtt;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Sets;
import com.hivemq.testcontainer.junit5.HiveMQTestContainerExtension;
import io.airbyte.commons.json.Jsons;
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
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.testcontainers.utility.DockerImageName;

@DisplayName("MqttRecordConsumer")
public class MqttRecordConsumerTest {

  @RegisterExtension
  public final HiveMQTestContainerExtension extension = new HiveMQTestContainerExtension(DockerImageName.parse("hivemq/hivemq-ce:2021.2"));

  @ParameterizedTest
  @ArgumentsSource(TopicMapArgumentsProvider.class)
  @SuppressWarnings("unchecked")
  public void testBuildTopicMap(final ConfiguredAirbyteCatalog catalog,
                                final String streamName,
                                final String namespace,
                                final String topicPattern,
                                final String expectedTopic) {
    final MqttDestinationConfig config = MqttDestinationConfig
        .getMqttDestinationConfig(getConfig(extension.getHost(), extension.getMqttPort(), topicPattern));

    final MqttRecordConsumer recordConsumer = new MqttRecordConsumer(config, catalog, mock(Consumer.class));
    final Map<AirbyteStreamNameNamespacePair, String> topicMap = recordConsumer.buildTopicMap();
    assertEquals(Sets.newHashSet(catalog.getStreams()).size(), topicMap.size());

    final AirbyteStreamNameNamespacePair streamNameNamespacePair = new AirbyteStreamNameNamespacePair(streamName, namespace);
    assertEquals(expectedTopic, topicMap.get(streamNameNamespacePair));
  }

  @Test
  @SuppressWarnings("unchecked")
  void testCannotConnectToBrokers() throws Exception {
    final MqttDestinationConfig config = MqttDestinationConfig
        .getMqttDestinationConfig(getConfig(extension.getHost(), extension.getMqttPort() + 10, "test-topic"));

    final String streamName = "test-stream";
    final String namespace = "test-schema";
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createConfiguredAirbyteStream(
            streamName,
            namespace,
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING))));
    final MqttRecordConsumer consumer = new MqttRecordConsumer(config, catalog, mock(Consumer.class));
    final List<AirbyteMessage> expectedRecords = getNRecords(10, streamName, namespace);

    assertThrows(RuntimeException.class, consumer::start);

    expectedRecords.forEach(m -> assertThrows(RuntimeException.class, () -> consumer.accept(m)));

    consumer.accept(new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(namespace + "." + streamName, 0)))));
    consumer.close();
  }

  private JsonNode getConfig(final String broker, final int port, final String topic) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("broker_host", broker)
        .put("broker_port", port)
        .put("use_tls", false)
        .put("topic_pattern", topic)
        .put("publisher_sync", true)
        .put("connect_timeout", 10)
        .put("automatic_reconnect", false)
        .put("clean_session", true)
        .put("message_retained", true)
        .put("message_qos", "EXACTLY_ONCE")
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
      final List<ConfiguredAirbyteCatalog> catalogs = new ArrayList<>();
      catalogs.add(new ConfiguredAirbyteCatalog().withStreams(List.of(stream1)));
      catalogs.add(new ConfiguredAirbyteCatalog().withStreams(List.of(stream1, stream1)));
      catalogs.add(new ConfiguredAirbyteCatalog().withStreams(List.of(stream1, stream2)));

      return catalogs.stream()
          .flatMap(catalog -> catalog.getStreams().stream()
              .map(stream -> buildArgs(catalog, stream.getStream()))
              .flatMap(Collection::stream));
    }

    private List<Arguments> buildArgs(final ConfiguredAirbyteCatalog catalog, final AirbyteStream stream) {
      return ImmutableList.of(
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), TOPIC_NAME, TOPIC_NAME),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "test-topic", "test-topic"),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "{namespace}", stream.getNamespace()),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "{stream}", stream.getName()),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "{namespace}.{stream}." + TOPIC_NAME,
              stream.getNamespace() + "." + stream.getName() + "." + TOPIC_NAME),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "{namespace}-{stream}-" + TOPIC_NAME,
              stream.getNamespace() + "-" + stream.getName() + "-" + TOPIC_NAME),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "topic with spaces", "topic with spaces"),
          Arguments.of(catalog, stream.getName(), stream.getNamespace(), "UppercaseTopic/test", "UppercaseTopic/test"));
    }

  }

}
