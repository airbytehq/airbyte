/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.config.Configs;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class ErrorReportingClientFactoryTest {

  @Test
  void testCreateErrorReportingClientLogging() {
    assertTrue(
        ErrorReportingClientFactory.getClient(
            Configs.ErrorReportingStrategy.LOGGING, Mockito.mock(Configs.class)) instanceof LoggingErrorReportingClient);
  }

  @Test
  void testCreateErrorReportingClientSentry() {
    final Configs configsMock = Mockito.mock(Configs.class);
    Mockito.when(configsMock.getErrorReportingSentryDSN()).thenReturn("");

    assertTrue(
        ErrorReportingClientFactory.getClient(
            Configs.ErrorReportingStrategy.SENTRY, configsMock) instanceof SentryErrorReportingClient);
  }

}
