/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yugabytedb;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class YugabytedbNamingTransformerTest {

  private YugabytedbNamingTransformer yugabytedbNamingTransformer;

  @BeforeEach
  void setup() {
    yugabytedbNamingTransformer = new YugabytedbNamingTransformer();
  }

  @Test
  void testApplyDefaultCase() {

    var defaultCase = yugabytedbNamingTransformer.applyDefaultCase("DEFAULT_CASE");

    assertThat(defaultCase).isEqualTo("default_case");

  }

}
