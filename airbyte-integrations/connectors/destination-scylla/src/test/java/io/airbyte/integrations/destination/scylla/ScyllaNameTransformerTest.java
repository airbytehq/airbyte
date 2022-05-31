/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class ScyllaNameTransformerTest {

  private ScyllaNameTransformer scyllaNameTransformer;

  @BeforeAll
  void setup() {
    var scyllaConfig = TestDataFactory.scyllaConfig("127.0.0.1", 9042);
    this.scyllaNameTransformer = new ScyllaNameTransformer(scyllaConfig);
  }

  @Test
  void testOutputTable() {

    var table = scyllaNameTransformer.outputTable("stream_name");

    assertThat(table).matches("airbyte_raw_stream_name");

  }

  @Test
  void testOutputTmpTable() {

    var table = scyllaNameTransformer.outputTmpTable("stream_name");

    assertThat(table).matches("airbyte_tmp_+[a-z]+_stream_name");

  }

  @Test
  void testOutputKeyspace() {

    var keyspace = scyllaNameTransformer.outputKeyspace("***keyspace^h");

    assertThat(keyspace).matches("keyspace_h");

  }

  @Test
  void outputColumn() {

    var column = scyllaNameTransformer.outputColumn("_airbyte_data");

    assertThat(column).matches("\"_airbyte_data\"");

  }

}
