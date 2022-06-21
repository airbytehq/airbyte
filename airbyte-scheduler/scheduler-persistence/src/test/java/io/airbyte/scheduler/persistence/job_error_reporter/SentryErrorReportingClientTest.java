/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import org.junit.Test;
import org.junit.jupiter.api.BeforeEach;

public class SentryErrorReportingClientTest {

  SentryErrorReportingClient sentryErrorReportingClient;

  @BeforeEach
  void setup() {
    sentryErrorReportingClient = new SentryErrorReportingClient();
  }

  @Test
  void testReport() {
    // TODO
  }

}
