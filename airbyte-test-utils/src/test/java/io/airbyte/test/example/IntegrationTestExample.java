/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.example;

import io.airbyte.test.annotations.IntegrationTest;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

/**
 * This is an example of an integration test
 */
@IntegrationTest
@Slf4j
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class IntegrationTestExample {

  @Test
  void longTest() {
    log.error("Start test - integration");
    log.error("end test - integration");
  }

}
