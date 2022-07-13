/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.datastax.driver.core.exceptions.InvalidQueryException;
import io.airbyte.integrations.util.HostPortResolver;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class ScyllaCqlProviderTest {

  private static final String SCYLLA_KEYSPACE = "scylla_keyspace";

  private static final String SCYLLA_TABLE = "scylla_table";

  private ScyllaCqlProvider scyllaCqlProvider;

  private ScyllaNameTransformer nameTransformer;

  @BeforeAll
  void setup() {
    var scyllaContainer = ScyllaContainerInitializr.initContainer();
    var scyllaConfig = TestDataFactory.scyllaConfig(
        HostPortResolver.resolveHost(scyllaContainer),
        HostPortResolver.resolvePort(scyllaContainer));
    this.scyllaCqlProvider = new ScyllaCqlProvider(scyllaConfig);
    this.nameTransformer = new ScyllaNameTransformer(scyllaConfig);
    this.scyllaCqlProvider.createKeyspaceIfNotExists(SCYLLA_KEYSPACE);
    this.scyllaCqlProvider.createTableIfNotExists(SCYLLA_KEYSPACE, SCYLLA_TABLE);
  }

  @AfterEach
  void clean() {
    scyllaCqlProvider.truncate(SCYLLA_KEYSPACE, SCYLLA_TABLE);
  }

  @Test
  void testCreateKeySpaceIfNotExists() {
    String keyspace = nameTransformer.outputKeyspace("test_keyspace");
    assertDoesNotThrow(() -> scyllaCqlProvider.createKeyspaceIfNotExists(keyspace));
  }

  @Test
  void testCreateTableIfNotExists() {
    String table = nameTransformer.outputTable("test_stream");
    assertDoesNotThrow(() -> scyllaCqlProvider.createTableIfNotExists(SCYLLA_KEYSPACE, table));
  }

  @Test
  void testInsert() {
    // given
    scyllaCqlProvider.insert(SCYLLA_KEYSPACE, SCYLLA_TABLE, "{\"property\":\"data1\"}");
    scyllaCqlProvider.insert(SCYLLA_KEYSPACE, SCYLLA_TABLE, "{\"property\":\"data2\"}");
    scyllaCqlProvider.insert(SCYLLA_KEYSPACE, SCYLLA_TABLE, "{\"property\":\"data3\"}");

    // when
    var resultSet = scyllaCqlProvider.select(SCYLLA_KEYSPACE, SCYLLA_TABLE);

    // then
    assertThat(resultSet)
        .isNotNull()
        .hasSize(3)
        .anyMatch(r -> r.value2().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.value2().equals("{\"property\":\"data2\"}"))
        .anyMatch(r -> r.value2().equals("{\"property\":\"data3\"}"));

  }

  @Test
  void testTruncate() {
    // given
    scyllaCqlProvider.insert(SCYLLA_KEYSPACE, SCYLLA_TABLE, "{\"property\":\"data1\"}");
    scyllaCqlProvider.insert(SCYLLA_KEYSPACE, SCYLLA_TABLE, "{\"property\":\"data2\"}");
    scyllaCqlProvider.insert(SCYLLA_KEYSPACE, SCYLLA_TABLE, "{\"property\":\"data3\"}");

    // when
    scyllaCqlProvider.truncate(SCYLLA_KEYSPACE, SCYLLA_TABLE);
    var resultSet = scyllaCqlProvider.select(SCYLLA_KEYSPACE, SCYLLA_TABLE);

    // then
    assertThat(resultSet)
        .isNotNull()
        .isEmpty();
  }

  @Test
  void testDropTableIfExists() {
    // given
    String table = nameTransformer.outputTmpTable("test_stream");
    scyllaCqlProvider.createTableIfNotExists(SCYLLA_KEYSPACE, table);

    // when
    scyllaCqlProvider.dropTableIfExists(SCYLLA_KEYSPACE, table);

    // then
    assertThrows(InvalidQueryException.class, () -> scyllaCqlProvider.select(SCYLLA_KEYSPACE, table));
  }

  @Test
  void testCopy() {
    // given
    String tmpTable = nameTransformer.outputTmpTable("test_stream_copy");
    scyllaCqlProvider.createTableIfNotExists(SCYLLA_KEYSPACE, tmpTable);
    scyllaCqlProvider.insert(SCYLLA_KEYSPACE, tmpTable, "{\"property\":\"data1\"}");
    scyllaCqlProvider.insert(SCYLLA_KEYSPACE, tmpTable, "{\"property\":\"data2\"}");
    scyllaCqlProvider.insert(SCYLLA_KEYSPACE, tmpTable, "{\"property\":\"data3\"}");

    String rawTable = nameTransformer.outputTable("test_stream_copy");
    scyllaCqlProvider.createTableIfNotExists(SCYLLA_KEYSPACE, rawTable);

    // when
    scyllaCqlProvider.copy(SCYLLA_KEYSPACE, tmpTable, rawTable);
    var resultSet = scyllaCqlProvider.select(SCYLLA_KEYSPACE, rawTable);

    // then
    assertThat(resultSet)
        .isNotNull()
        .hasSize(3)
        .anyMatch(r -> r.value2().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.value2().equals("{\"property\":\"data2\"}"))
        .anyMatch(r -> r.value2().equals("{\"property\":\"data3\"}"));

  }

}
