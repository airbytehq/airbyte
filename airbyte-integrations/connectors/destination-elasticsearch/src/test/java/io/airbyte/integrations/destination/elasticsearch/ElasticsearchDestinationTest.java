/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.elasticsearch.ElasticsearchContainer;

public class ElasticsearchDestinationTest {

  private static final Logger log = LoggerFactory.getLogger(ElasticsearchDestinationTest.class);

  private static ElasticsearchContainer container;
  private static JsonNode config;

  @BeforeAll
  public static void beforeAll() {
    container = new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:7.15.1")
        .withEnv("ES_JAVA_OPTS", "-Xms256m -Xmx256m")
        .withEnv("discovery.type", "single-node")
        .withEnv("network.host", "0.0.0.0")
        .withExposedPorts(9200)
        .withStartupTimeout(Duration.ofSeconds(60));
    container.start();
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("endpoint", String.format("http://%s:%s", container.getHost(), container.getMappedPort(9200)))
        .build());
  }

  @AfterAll
  public static void afterAll() {
    container.stop();
    container.close();
  }

  @Test
  public void withAppend() throws Exception {

    var primaryKey = new ArrayList<List<String>>();
    primaryKey.add(List.of("id"));

    final var namespace = "public";
    final var streamName = "appended_records";
    final var testConfig = new TestConfig(namespace, streamName, DestinationSyncMode.APPEND, primaryKey);
    final var testMessages = generateTestMessages(namespace, streamName, 0, 10);
    final var firstRecordSet = e2e(testConfig, testMessages);

    assertEquals(
        testMessages.stream().map(AirbyteMessage::getRecord).map(AirbyteRecordMessage::getData).collect(Collectors.toList()),
        firstRecordSet);

    final var secondRecordSet = e2e(testConfig, testMessages);
    assertEquals(testMessages.size() * 2, secondRecordSet.size(), "it should have appended the test messages twice");
  }

  @Test
  public void withOverwrite() throws Exception {
    var primaryKey = new ArrayList<List<String>>();
    primaryKey.add(List.of("id"));

    final var namespace = "public";
    final var streamName = "overwritten_records";
    final var testConfig = new TestConfig(namespace, streamName, DestinationSyncMode.OVERWRITE, primaryKey);
    final var testMessages = generateTestMessages(namespace, streamName, 0, 10);
    final var firstRecordSet = e2e(testConfig, testMessages);

    assertEquals(
        testMessages.stream().map(AirbyteMessage::getRecord).map(AirbyteRecordMessage::getData).collect(Collectors.toList()),
        firstRecordSet);

    final var secondRecordSet = e2e(testConfig, testMessages);
    assertEquals(testMessages.size(), secondRecordSet.size(), "it should only have 1 set of test messages");
  }

  @Test
  public void withAppendDedup() throws Exception {
    var primaryKey = new ArrayList<List<String>>();
    primaryKey.add(List.of("id"));

    final var namespace = "public";
    final var streamName = "appended_and_deduped_records";
    final var testConfig = new TestConfig(namespace, streamName, DestinationSyncMode.APPEND_DEDUP, primaryKey);
    final var firstTestMessages = generateTestMessages(namespace, streamName, 0, 10);
    final var firstRecordSet = e2e(testConfig, firstTestMessages);

    assertEquals(
        firstTestMessages.stream().map(AirbyteMessage::getRecord).map(AirbyteRecordMessage::getData).collect(Collectors.toList()),
        firstRecordSet);

    final var secondTestMessages = generateTestMessages(namespace, streamName, 5, 15);

    final var secondRecordSet = e2e(testConfig, secondTestMessages);
    assertEquals(15, secondRecordSet.size(), "it should upsert records with matching primary keys");
  }

  private List<JsonNode> e2e(final TestConfig testConfig, final List<AirbyteMessage> testMessages) throws Exception {
    final var catalog = testConfig.getCatalog();
    final var namespace = testConfig.getNamespace();
    final var streamName = testConfig.getStreamName();
    final var indexName = testConfig.getIndexName();
    final var destination = new ElasticsearchDestination();

    final var check = destination.check(config);
    log.info("check status: {}", check);

    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.start();
    testMessages.forEach(m -> {
      try {
        consumer.accept(m);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
    consumer.accept(new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(namespace + "." + streamName, testMessages.size())))));
    consumer.close();

    final var connection = new ElasticsearchConnection(ConnectorConfiguration.fromJsonNode(config));

    final List<JsonNode> actualRecords =
        connection.getRecords(indexName);

    for (var record : actualRecords) {
      log.info("actual record: {}", record);
    }

    return actualRecords;
  }

  // generate some messages. Taken from the postgres destination test
  private List<AirbyteMessage> generateTestMessages(final String namespace, final String streamName, final int start, final int end) {
    return IntStream.range(start, end)
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

  private static class TestConfig extends ElasticsearchWriteConfig {

    public TestConfig(String namespace, String streamName, DestinationSyncMode destinationSyncMode, ArrayList<List<String>> primaryKey) {
      super(namespace, streamName, destinationSyncMode, primaryKey, false);
    }

    ConfiguredAirbyteCatalog getCatalog() {
      return new ConfiguredAirbyteCatalog().withStreams(List.of(
          CatalogHelpers.createConfiguredAirbyteStream(
              this.getStreamName(),
              this.getNamespace(),
              Field.of("id", JsonSchemaType.NUMBER),
              Field.of("name", JsonSchemaType.STRING))
              .withDestinationSyncMode(this.getSyncMode())
              .withPrimaryKey(this.getPrimaryKey())));
    }

  }

}
