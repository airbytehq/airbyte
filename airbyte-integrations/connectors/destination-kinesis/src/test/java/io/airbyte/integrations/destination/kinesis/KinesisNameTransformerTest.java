/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class KinesisNameTransformerTest {

  private KinesisNameTransformer kinesisNameTransformer;

  @BeforeEach
  void setup() {
    this.kinesisNameTransformer = new KinesisNameTransformer();
  }

  @Test
  void outputStream() {

    var column = kinesisNameTransformer.streamName("namespace", "stream");

    assertThat(column).matches("namespace_stream");

  }

  @Test
  void outputStreamConvert() {

    var keyspace = kinesisNameTransformer.streamName("**namespace^h", "##stream");

    assertThat(keyspace).matches("__namespace_h___stream");

  }

}
