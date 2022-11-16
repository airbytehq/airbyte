/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class RedpandaNameTransformerTest {

  @Test
  void testTransformTopicName() {

    var redpandaNameTransformer = new RedpandaNameTransformer();

    String topicName = redpandaNameTransformer.topicName("namespace", "stream");

    assertThat(topicName).isEqualTo("namespace_stream");

  }

}
