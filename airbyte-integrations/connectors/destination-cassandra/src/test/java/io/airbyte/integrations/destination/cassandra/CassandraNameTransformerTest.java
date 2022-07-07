/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CassandraNameTransformerTest {

  private CassandraNameTransformer cassandraNameTransformer;

  @BeforeAll
  void setup() {
    var cassandraConfig = TestDataFactory.createCassandraConfig(
        "usr",
        "pw",
        "127.0.0.1",
        9042);
    this.cassandraNameTransformer = new CassandraNameTransformer(cassandraConfig);
  }

  @Test
  void testOutputTable() {

    var table = cassandraNameTransformer.outputTable("stream_name");

    assertThat(table).matches("airbyte_raw_stream_name");

  }

  @Test
  void testOutputTmpTable() {

    var table = cassandraNameTransformer.outputTmpTable("stream_name");

    assertThat(table).matches("airbyte_tmp_+[a-z]+_stream_name");

  }

  @Test
  void testOutputKeyspace() {

    var keyspace = cassandraNameTransformer.outputKeyspace("***keyspace^h");

    assertThat(keyspace).matches("keyspace_h");

  }

  @Test
  void outputColumn() {

    var column = cassandraNameTransformer.outputColumn("_airbyte_data");

    assertThat(column).matches("\"_airbyte_data\"");

  }

}
