/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.kafka;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.jackson.MoreMappers;
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
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;

@DisplayName("KafkaRecordConsumer")
public class KafkaRecordConsumerTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();
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

  @ParameterizedTest
  @ArgumentsSource(TopicMapArgumentsProvider.class)
  @SuppressWarnings("unchecked")
  public void testBuildTopicMap(String topicPattern, String expectedTopic) {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(topicPattern));
    final KafkaRecordConsumer recordConsumer = new KafkaRecordConsumer(config, CATALOG, mock(Consumer.class), NAMING_RESOLVER);

    final Map<AirbyteStreamNameNamespacePair, String> topicMap = recordConsumer.buildTopicMap();
    assertEquals(1, topicMap.size());

    final AirbyteStreamNameNamespacePair streamNameNamespacePair = new AirbyteStreamNameNamespacePair(STREAM_NAME, SCHEMA_NAME);
    assertEquals(expectedTopic, topicMap.get(streamNameNamespacePair));
  }

  @Test
  @SuppressWarnings("unchecked")
  void testCannotConnectToBrokers() throws Exception {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    final KafkaRecordConsumer consumer = new KafkaRecordConsumer(config, CATALOG, mock(Consumer.class), NAMING_RESOLVER);
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    consumer.start();

    expectedRecords.forEach(m -> assertThrows(RuntimeException.class, () -> consumer.accept(m)));

    consumer.accept(new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(SCHEMA_NAME + "." + STREAM_NAME, 0)))));
    consumer.close();
  }

  private JsonNode getConfig(String topicPattern) {
    ObjectNode stubProtocolConfig = mapper.createObjectNode();
    stubProtocolConfig.put("security_protocol", KafkaProtocol.PLAINTEXT.toString());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", "localhost:9092")
        .put("topic_pattern", topicPattern)
        .put("sync_producer", true)
        .put("protocol", stubProtocolConfig)
        .put("sasl_jaas_config", "")
        .put("sasl_mechanism", "PLAIN")
        .put("client_id", "test-client")
        .put("acks", "all")
        .put("transactional_id", "txn-id")
        .put("enable_idempotence", true)
        .put("compression_type", "none")
        .put("batch_size", "16384")
        .put("linger_ms", "0")
        .put("max_in_flight_requests_per_connection", "5")
        .put("client_dns_lookup", "use_all_dns_ips")
        .put("buffer_memory", 33554432)
        .put("max_request_size", 1048576)
        .put("retries", 1)
        .put("socket_connection_setup_timeout_ms", "10")
        .put("socket_connection_setup_timeout_max_ms", "30")
        .put("max_block_ms", "100")
        .put("request_timeout_ms", 100)
        .put("delivery_timeout_ms", 120)
        .put("send_buffer_bytes", -1)
        .put("receive_buffer_bytes", -1)
        .build());
  }

  private List<AirbyteMessage> getNRecords(int n) {
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
    public Stream<? extends Arguments> provideArguments(ExtensionContext context) {
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

}
