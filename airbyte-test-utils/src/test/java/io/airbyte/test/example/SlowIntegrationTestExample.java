/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.example;

import io.airbyte.test.annotations.IntegrationTest;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

/**
 * This is an example of a slow integration test
 */
@IntegrationTest
@Slf4j
public class SlowIntegrationTestExample {

  @Test
  public void longTest() {
    log.error("Start test - slow integration");
    log.error("end test - slow integration");
  }

}
