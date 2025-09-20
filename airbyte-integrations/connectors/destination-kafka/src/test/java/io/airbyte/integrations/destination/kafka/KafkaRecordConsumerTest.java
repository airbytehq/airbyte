/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.commons.jackson.MoreMappers;
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
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;
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

@DisplayName("KafkaRecordConsumer")
@ExtendWith(MockitoExtension.class)
public class KafkaRecordConsumerTest extends PerStreamStateMessageTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();
  private static final String TOPIC_NAME = "test.topic";
  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";

  private static final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createConfiguredAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING))));

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  private KafkaRecordConsumer consumer;

  private static final StandardNameTransformer NAMING_RESOLVER = new StandardNameTransformer();

  @BeforeEach
  public void init() {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    consumer = new KafkaRecordConsumer(config, CATALOG, outputRecordCollector, NAMING_RESOLVER);
  }

  @ParameterizedTest
  @ArgumentsSource(TopicMapArgumentsProvider.class)
  @SuppressWarnings("unchecked")
  public void testBuildTopicMap(final String topicPattern, final String expectedTopic) {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(topicPattern));
    consumer = new KafkaRecordConsumer(config, CATALOG, outputRecordCollector, NAMING_RESOLVER);

    final Map<AirbyteStreamNameNamespacePair, String> topicMap = consumer.buildTopicMap();
    assertEquals(1, topicMap.size());

    final AirbyteStreamNameNamespacePair streamNameNamespacePair = new AirbyteStreamNameNamespacePair(STREAM_NAME, SCHEMA_NAME);
    assertEquals(expectedTopic, topicMap.get(streamNameNamespacePair));
  }

  @Test
  @SuppressWarnings("unchecked")
  void testCannotConnectToBrokers() throws Exception {
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    consumer.start();

    expectedRecords.forEach(m -> assertThrows(RuntimeException.class, () -> consumer.accept(m)));

    consumer.accept(new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(SCHEMA_NAME + "." + STREAM_NAME, 0)))));
    consumer.close();
  }

  private JsonNode getConfig(final String topicPattern) {
    final ObjectNode stubProtocolConfig = mapper.createObjectNode();
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

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return consumer;
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

  @Test
  @DisplayName("Test building primary key map from catalog")
  public void testBuildPrimaryKeyMap() {
    // Create a catalog with primary keys
    final AirbyteStream streamWithPK = CatalogHelpers.createAirbyteStream(
        STREAM_NAME,
        SCHEMA_NAME,
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("name", JsonSchemaType.STRING));
    streamWithPK.setSourceDefinedPrimaryKey(List.of(List.of("id")));

    final ConfiguredAirbyteStream configuredStream = new ConfiguredAirbyteStream()
        .withStream(streamWithPK);

    final ConfiguredAirbyteCatalog catalogWithPK = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(configuredStream));

    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    final KafkaRecordConsumer consumerWithPK = new KafkaRecordConsumer(config, catalogWithPK, outputRecordCollector, NAMING_RESOLVER);

    final Map<AirbyteStreamNameNamespacePair, List<List<String>>> primaryKeyMap = consumerWithPK.buildPrimaryKeyMap();

    assertEquals(1, primaryKeyMap.size());
    final AirbyteStreamNameNamespacePair streamPair = new AirbyteStreamNameNamespacePair(STREAM_NAME, SCHEMA_NAME);
    assertEquals(List.of(List.of("id")), primaryKeyMap.get(streamPair));
  }

  @Test
  @DisplayName("Test building primary key map with composite keys")
  public void testBuildPrimaryKeyMapComposite() {
    // Create a catalog with composite primary keys
    final AirbyteStream streamWithCompositePK = CatalogHelpers.createAirbyteStream(
        STREAM_NAME,
        SCHEMA_NAME,
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("tenant_id", JsonSchemaType.NUMBER),
        Field.of("name", JsonSchemaType.STRING));
    streamWithCompositePK.setSourceDefinedPrimaryKey(List.of(List.of("tenant_id"), List.of("id")));

    final ConfiguredAirbyteStream configuredStream = new ConfiguredAirbyteStream()
        .withStream(streamWithCompositePK);

    final ConfiguredAirbyteCatalog catalogWithPK = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(configuredStream));

    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    final KafkaRecordConsumer consumerWithPK = new KafkaRecordConsumer(config, catalogWithPK, outputRecordCollector, NAMING_RESOLVER);

    final Map<AirbyteStreamNameNamespacePair, List<List<String>>> primaryKeyMap = consumerWithPK.buildPrimaryKeyMap();

    assertEquals(1, primaryKeyMap.size());
    final AirbyteStreamNameNamespacePair streamPair = new AirbyteStreamNameNamespacePair(STREAM_NAME, SCHEMA_NAME);
    assertEquals(List.of(List.of("tenant_id"), List.of("id")), primaryKeyMap.get(streamPair));
  }

  @Test
  @DisplayName("Test building primary key map with user-configured primary key")
  public void testBuildPrimaryKeyMapUserConfigured() {
    // Create a catalog where user overrides source-defined primary key
    final AirbyteStream stream = CatalogHelpers.createAirbyteStream(
        STREAM_NAME,
        SCHEMA_NAME,
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("email", JsonSchemaType.STRING));
    stream.setSourceDefinedPrimaryKey(List.of(List.of("id")));

    final ConfiguredAirbyteStream configuredStream = new ConfiguredAirbyteStream()
        .withStream(stream)
        .withPrimaryKey(List.of(List.of("email"))); // User overrides with email as PK

    final ConfiguredAirbyteCatalog catalogWithPK = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(configuredStream));

    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    final KafkaRecordConsumer consumerWithPK = new KafkaRecordConsumer(config, catalogWithPK, outputRecordCollector, NAMING_RESOLVER);

    final Map<AirbyteStreamNameNamespacePair, List<List<String>>> primaryKeyMap = consumerWithPK.buildPrimaryKeyMap();

    final AirbyteStreamNameNamespacePair streamPair = new AirbyteStreamNameNamespacePair(STREAM_NAME, SCHEMA_NAME);
    assertEquals(List.of(List.of("email")), primaryKeyMap.get(streamPair)); // Should use user-configured PK
  }

  @Test
  @DisplayName("Test extractCdcOperation for insert")
  public void testExtractCdcOperationInsert() {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    final KafkaRecordConsumer testConsumer = new KafkaRecordConsumer(config, CATALOG, outputRecordCollector, NAMING_RESOLVER);

    final JsonNode dataWithLsn = Jsons.jsonNode(ImmutableMap.of(
        "id", 1,
        "name", "test",
        "_ab_cdc_lsn", "0/1234567"));

    assertEquals("insert", testConsumer.extractCdcOperation(dataWithLsn));
  }

  @Test
  @DisplayName("Test extractCdcOperation for update")
  public void testExtractCdcOperationUpdate() {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    final KafkaRecordConsumer testConsumer = new KafkaRecordConsumer(config, CATALOG, outputRecordCollector, NAMING_RESOLVER);

    final JsonNode dataWithUpdate = Jsons.jsonNode(ImmutableMap.of(
        "id", 1,
        "name", "test",
        "_ab_cdc_updated_at", "2023-01-01T00:00:00Z"));

    assertEquals("update", testConsumer.extractCdcOperation(dataWithUpdate));
  }

  @Test
  @DisplayName("Test extractCdcOperation for delete")
  public void testExtractCdcOperationDelete() {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    final KafkaRecordConsumer testConsumer = new KafkaRecordConsumer(config, CATALOG, outputRecordCollector, NAMING_RESOLVER);

    final JsonNode dataWithDelete = Jsons.jsonNode(ImmutableMap.of(
        "id", 1,
        "name", "test",
        "_ab_cdc_deleted_at", "2023-01-01T00:00:00Z"));

    assertEquals("delete", testConsumer.extractCdcOperation(dataWithDelete));
  }

  @Test
  @DisplayName("Test extractCdcOperation for non-CDC data")
  public void testExtractCdcOperationNonCdc() {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    final KafkaRecordConsumer testConsumer = new KafkaRecordConsumer(config, CATALOG, outputRecordCollector, NAMING_RESOLVER);

    final JsonNode regularData = Jsons.jsonNode(ImmutableMap.of(
        "id", 1,
        "name", "test"));

    assertNull(testConsumer.extractCdcOperation(regularData));
  }

  @Test
  @DisplayName("Test extractCdcOperation with null CDC fields")
  public void testExtractCdcOperationNullFields() {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    final KafkaRecordConsumer testConsumer = new KafkaRecordConsumer(config, CATALOG, outputRecordCollector, NAMING_RESOLVER);

    final ObjectNode dataWithNullDelete = mapper.createObjectNode();
    dataWithNullDelete.put("id", 1);
    dataWithNullDelete.put("name", "test");
    dataWithNullDelete.putNull("_ab_cdc_deleted_at");
    dataWithNullDelete.put("_ab_cdc_updated_at", "2023-01-01T00:00:00Z");

    // Should return "update" since deleted_at is null but updated_at is present
    assertEquals("update", testConsumer.extractCdcOperation(dataWithNullDelete));
  }

}
