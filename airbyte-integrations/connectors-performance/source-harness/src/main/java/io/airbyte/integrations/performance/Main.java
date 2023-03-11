/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.performance;

import com.fasterxml.jackson.core.JsonProcessingException;

public class Main {

  public static void main(final String[] args) {
    try {
      final PerformanceTest test = new PerformanceTest(null, null, null);
    } catch (final JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

}
