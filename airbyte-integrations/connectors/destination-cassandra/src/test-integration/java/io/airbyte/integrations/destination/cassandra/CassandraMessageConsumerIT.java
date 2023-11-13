/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.function.Function;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestMethodOrder;

@TestMethodOrder(OrderAnnotation.class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CassandraMessageConsumerIT {

  private static final String AIRBYTE_NAMESPACE_1 = "airbyte_namespace_1";
  private static final String AIRBYTE_NAMESPACE_2 = "airbyte_namespace_2";

  private static final String AIRBYTE_STREAM_1 = "airbyte_stream_1";
  private static final String AIRBYTE_STREAM_2 = "airbyte_stream_2";

  private CassandraContainerInitializr.ConfiguredCassandraContainer cassandraContainer;

  private CassandraConfig cassandraConfig;

  private CassandraMessageConsumer cassandraMessageConsumer;

  private CassandraNameTransformer nameTransformer;

  @BeforeAll
  void setup() {
    cassandraContainer = CassandraContainerInitializr.initContainer();
    cassandraConfig = TestDataFactory.createCassandraConfig(
        cassandraContainer.getUsername(),
        cassandraContainer.getPassword(),
        cassandraContainer.getHost(),
        cassandraContainer.getFirstMappedPort());

    final var stream1 = TestDataFactory.createAirbyteStream(AIRBYTE_STREAM_1, AIRBYTE_NAMESPACE_1);
    final var stream2 = TestDataFactory.createAirbyteStream(AIRBYTE_STREAM_2, AIRBYTE_NAMESPACE_2);

    final var cStream1 = TestDataFactory.createConfiguredAirbyteStream(DestinationSyncMode.APPEND, stream1);
    final var cStream2 = TestDataFactory.createConfiguredAirbyteStream(DestinationSyncMode.OVERWRITE, stream2);

    final var catalog = TestDataFactory.createConfiguredAirbyteCatalog(cStream1, cStream2);

    final CassandraCqlProvider cassandraCqlProvider = new CassandraCqlProvider(cassandraConfig);
    cassandraMessageConsumer = new CassandraMessageConsumer(cassandraConfig, catalog, cassandraCqlProvider, message -> {});
    nameTransformer = new CassandraNameTransformer(cassandraConfig);
  }

  @AfterAll
  void close() {
    cassandraContainer.close();
  }

  @Test
  @Order(1)
  void testStartTracked() {
    assertDoesNotThrow(() -> cassandraMessageConsumer.startTracked());
  }

  @Test
  @Order(2)
  void testAcceptTracked() {

    final Function<String, JsonNode> function =
        data -> Jsons.jsonNode(ImmutableMap.builder().put("property", data).build());

    assertDoesNotThrow(() -> {
      cassandraMessageConsumer.acceptTracked(
          TestDataFactory.createAirbyteMessage(AirbyteMessage.Type.RECORD, AIRBYTE_STREAM_1, AIRBYTE_NAMESPACE_1,
              function.apply("data1")));
      cassandraMessageConsumer.acceptTracked(
          TestDataFactory.createAirbyteMessage(AirbyteMessage.Type.RECORD, AIRBYTE_STREAM_1, AIRBYTE_NAMESPACE_1,
              function.apply("data2")));
      cassandraMessageConsumer.acceptTracked(
          TestDataFactory.createAirbyteMessage(AirbyteMessage.Type.RECORD, AIRBYTE_STREAM_2, AIRBYTE_NAMESPACE_2,
              function.apply("data3")));
      cassandraMessageConsumer.acceptTracked(
          TestDataFactory.createAirbyteMessage(AirbyteMessage.Type.RECORD, AIRBYTE_STREAM_2, AIRBYTE_NAMESPACE_2,
              function.apply("data4")));
      cassandraMessageConsumer.acceptTracked(
          TestDataFactory.createAirbyteMessage(AirbyteMessage.Type.STATE, AIRBYTE_STREAM_2, AIRBYTE_NAMESPACE_2,
              function.apply("data5")));
    });

  }

  @Test
  @Order(3)
  void testClose() {

    assertDoesNotThrow(() -> cassandraMessageConsumer.close(false));

  }

  @Test
  @Order(4)
  void testFinalState() {
    final var keyspace1 = nameTransformer.outputKeyspace(AIRBYTE_NAMESPACE_1);
    final var keyspace2 = nameTransformer.outputKeyspace(AIRBYTE_NAMESPACE_2);
    final var table1 = nameTransformer.outputTable(AIRBYTE_STREAM_1);
    final var table2 = nameTransformer.outputTable(AIRBYTE_STREAM_2);
    try (final var cassandraCqlProvider = new CassandraCqlProvider(cassandraConfig)) {
      final var resultSet1 = cassandraCqlProvider.select(keyspace1, table1);
      final var resultSet2 = cassandraCqlProvider.select(keyspace2, table2);
      assertThat(resultSet1)
          .isNotNull()
          .hasSize(2)
          .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
          .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"));

      assertThat(resultSet2)
          .isNotNull()
          .hasSize(2)
          .anyMatch(r -> r.getData().equals("{\"property\":\"data3\"}"))
          .anyMatch(r -> r.getData().equals("{\"property\":\"data4\"}"));
    }
  }

}
