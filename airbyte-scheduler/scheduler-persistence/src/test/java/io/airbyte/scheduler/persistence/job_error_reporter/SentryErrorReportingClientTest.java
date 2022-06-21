/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SentryErrorReportingClientTest {

  SentryErrorReportingClient sentryErrorReportingClient;

  @BeforeEach
  void setup() {
    sentryErrorReportingClient = new SentryErrorReportingClient("");
  }

  @Test
  void testReport() {
    // TODO
    Assertions.assertEquals(1, 1);
  }

}
