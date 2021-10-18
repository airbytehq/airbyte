package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.*;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.elasticsearch.ElasticsearchContainer;

import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class ElasticsearchDestinationTest {

    private static final Logger log = LoggerFactory.getLogger(ElasticsearchDestinationTest.class);

    private static ElasticsearchContainer container;
    private static final String NAMESPACE = "public";
    private static final String STREAM_NAME = "id_and_name";
    private static final String INDEX_NAME = ElasticsearchAirbyteMessageConsumerFactory.streamToIndexName(NAMESPACE, STREAM_NAME);

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

    @AfterEach
    public void afterEach() throws Exception {
        final var connection = new ElasticsearchConnection(ConnectorConfiguration.FromJsonNode(config));
        //connection.deleteIndexIfPresent(INDEX_NAME);
    }

    @Test
    public void withAppend() throws Exception {
        e2e(getCatalog(DestinationSyncMode.APPEND));
    }

    @Test
    public void withOverwrite() throws Exception {
       e2e(getCatalog(DestinationSyncMode.OVERWRITE));
    }

    @Test
    public void withAppendDedup() throws Exception {
        e2e(getCatalog(DestinationSyncMode.APPEND_DEDUP));
    }

    private ConfiguredAirbyteCatalog getCatalog(DestinationSyncMode destinationSyncMode) {
        var primaryKey = new ArrayList<List<String>>();
        primaryKey.add(List.of("id"));
        return new ConfiguredAirbyteCatalog().withStreams(List.of(
                        CatalogHelpers.createConfiguredAirbyteStream(
                                        STREAM_NAME,
                                        NAMESPACE,
                                        Field.of("id", JsonSchemaPrimitive.NUMBER),
                                        Field.of("name", JsonSchemaPrimitive.STRING))
                                .withDestinationSyncMode(destinationSyncMode)
                                .withPrimaryKey(primaryKey)
                )
        );
    }

    private void e2e(ConfiguredAirbyteCatalog catalog) throws Exception {
        var destination = new ElasticsearchDestination();

        var check = destination.check(config);
        log.info("check status: {}", check);

        final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);
        final List<AirbyteMessage> expectedRecords = getNRecords(10);

        consumer.start();
        expectedRecords.forEach(m -> {
            try {
                consumer.accept(m);
            } catch (final Exception e) {
                throw new RuntimeException(e);
            }
        });
        consumer.accept(new AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(NAMESPACE + "." + STREAM_NAME, 10)))));
        consumer.close();

        final var connection = new ElasticsearchConnection(ConnectorConfiguration.FromJsonNode(config));

        final List<JsonNode> actualRecords =
                connection.getRecords(INDEX_NAME);

        for (var record :
                actualRecords) {
            log.info("actual record: {}", record);
        }
        assertEquals(
                expectedRecords.stream().map(AirbyteMessage::getRecord).map(AirbyteRecordMessage::getData).collect(Collectors.toList()),
                actualRecords);
    }

    // generate some messages. Taken from the postgres destination test
    private List<AirbyteMessage> getNRecords(final int n) {
        return IntStream.range(0, n)
                .boxed()
                .map(i -> new AirbyteMessage()
                        .withType(AirbyteMessage.Type.RECORD)
                        .withRecord(new AirbyteRecordMessage()
                                .withStream(STREAM_NAME)
                                .withNamespace(NAMESPACE)
                                .withEmittedAt(Instant.now().toEpochMilli())
                                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
                .collect(Collectors.toList());
    }
}
