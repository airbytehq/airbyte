/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.datastax.oss.driver.api.core.servererrors.InvalidQueryException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CassandraCqlProviderIT {

  private static final String CASSANDRA_KEYSPACE = "cassandra_keyspace";

  private static final String CASSANDRA_TABLE = "cassandra_table";

  private CassandraCqlProvider cassandraCqlProvider;

  private CassandraNameTransformer nameTransformer;

  @BeforeAll
  void setup() {
    var cassandraContainer = CassandraContainerInitializr.initContainer();
    var cassandraConfig = TestDataFactory.createCassandraConfig(
        cassandraContainer.getUsername(),
        cassandraContainer.getPassword(),
        cassandraContainer.getHost(),
        cassandraContainer.getFirstMappedPort());
    this.cassandraCqlProvider = new CassandraCqlProvider(cassandraConfig);
    this.nameTransformer = new CassandraNameTransformer(cassandraConfig);
    cassandraCqlProvider.createKeySpaceIfNotExists(CASSANDRA_KEYSPACE, 1);
    cassandraCqlProvider.createTableIfNotExists(CASSANDRA_KEYSPACE, CASSANDRA_TABLE);
  }

  @AfterEach
  void clean() {
    cassandraCqlProvider.truncate(CASSANDRA_KEYSPACE, CASSANDRA_TABLE);
  }

  @Test
  void testCreateKeySpaceIfNotExists() {
    String keyspace = nameTransformer.outputKeyspace("test_keyspace");
    assertDoesNotThrow(() -> cassandraCqlProvider.createKeySpaceIfNotExists(keyspace, 1));
  }

  @Test
  void testCreateTableIfNotExists() {
    String table = nameTransformer.outputTable("test_stream");
    assertDoesNotThrow(() -> cassandraCqlProvider.createTableIfNotExists(CASSANDRA_KEYSPACE, table));
  }

  @Test
  void testInsert() {
    // given
    cassandraCqlProvider.insert(CASSANDRA_KEYSPACE, CASSANDRA_TABLE, "{\"property\":\"data1\"}");
    cassandraCqlProvider.insert(CASSANDRA_KEYSPACE, CASSANDRA_TABLE, "{\"property\":\"data2\"}");
    cassandraCqlProvider.insert(CASSANDRA_KEYSPACE, CASSANDRA_TABLE, "{\"property\":\"data3\"}");

    // when
    var resultSet = cassandraCqlProvider.select(CASSANDRA_KEYSPACE, CASSANDRA_TABLE);

    // then
    assertThat(resultSet)
        .isNotNull()
        .hasSize(3)
        .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data3\"}"));

  }

  @Test
  void testTruncate() {
    // given
    cassandraCqlProvider.insert(CASSANDRA_KEYSPACE, CASSANDRA_TABLE, "{\"property\":\"data1\"}");
    cassandraCqlProvider.insert(CASSANDRA_KEYSPACE, CASSANDRA_TABLE, "{\"property\":\"data2\"}");
    cassandraCqlProvider.insert(CASSANDRA_KEYSPACE, CASSANDRA_TABLE, "{\"property\":\"data3\"}");

    // when
    cassandraCqlProvider.truncate(CASSANDRA_KEYSPACE, CASSANDRA_TABLE);
    var resultSet = cassandraCqlProvider.select(CASSANDRA_KEYSPACE, CASSANDRA_TABLE);

    // then
    assertThat(resultSet)
        .isNotNull()
        .isEmpty();
  }

  @Test
  void testDropTableIfExists() {
    // given
    String table = nameTransformer.outputTmpTable("test_stream");
    cassandraCqlProvider.createTableIfNotExists(CASSANDRA_KEYSPACE, table);

    // when
    cassandraCqlProvider.dropTableIfExists(CASSANDRA_KEYSPACE, table);

    // then
    assertThrows(InvalidQueryException.class, () -> cassandraCqlProvider.select(CASSANDRA_KEYSPACE, table));
  }

  @Test
  void testCopy() {
    // given
    String tmpTable = nameTransformer.outputTmpTable("test_stream_copy");
    cassandraCqlProvider.createTableIfNotExists(CASSANDRA_KEYSPACE, tmpTable);
    cassandraCqlProvider.insert(CASSANDRA_KEYSPACE, tmpTable, "{\"property\":\"data1\"}");
    cassandraCqlProvider.insert(CASSANDRA_KEYSPACE, tmpTable, "{\"property\":\"data2\"}");
    cassandraCqlProvider.insert(CASSANDRA_KEYSPACE, tmpTable, "{\"property\":\"data3\"}");

    String rawTable = nameTransformer.outputTable("test_stream_copy");
    cassandraCqlProvider.createTableIfNotExists(CASSANDRA_KEYSPACE, rawTable);

    // when
    cassandraCqlProvider.copy(CASSANDRA_KEYSPACE, tmpTable, rawTable);
    var resultSet = cassandraCqlProvider.select(CASSANDRA_KEYSPACE, rawTable);

    // then
    assertThat(resultSet)
        .isNotNull()
        .hasSize(3)
        .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data3\"}"));

  }

}
