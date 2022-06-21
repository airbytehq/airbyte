/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.config.Configs;
import org.junit.jupiter.api.Test;

public class ErrorReportingClientFactoryTest {

  @Test
  void testCreateErrorReportingClientLogging() {
    assertTrue(
        ErrorReportingClientFactory.getClient(
            Configs.ErrorReportingStrategy.LOGGING) instanceof LoggingErrorReportingClient);
  }

  @Test
  void testCreateErrorReportingClientSentry() {
    assertTrue(
        ErrorReportingClientFactory.getClient(
            Configs.ErrorReportingStrategy.SENTRY) instanceof SentryErrorReportingClient);
  }

}
