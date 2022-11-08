/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import static org.assertj.core.api.Assertions.assertThat;

import java.net.URI;
import java.net.URISyntaxException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class KinesisConfigTest {

  private KinesisConfig kinesisConfig;

  @BeforeEach
  void setup() {
    var jsonConfig = KinesisDataFactory.jsonConfig(
        "http://aws.kinesis.com",
        "eu-west-1",
        "random_access_key",
        "random_secret_key");
    this.kinesisConfig = new KinesisConfig(jsonConfig);
  }

  @Test
  void testConfig() throws URISyntaxException {

    assertThat(kinesisConfig)
        .hasFieldOrPropertyWithValue("endpoint", new URI("http://aws.kinesis.com"))
        .hasFieldOrPropertyWithValue("region", "eu-west-1")
        .hasFieldOrPropertyWithValue("shardCount", 5)
        .hasFieldOrPropertyWithValue("accessKey", "random_access_key")
        .hasFieldOrPropertyWithValue("privateKey", "random_secret_key")
        .hasFieldOrPropertyWithValue("bufferSize", 100);

  }

}
