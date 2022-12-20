/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test.logging;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

public interface TestingLogger {

  enum LoggingType {
    FirstN,
    EveryNth,
    RandomSampling
  }

  void log(AirbyteRecordMessage recordMessage);

}
