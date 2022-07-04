/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.config.Configs;
import io.airbyte.config.Configs.JobErrorReportingStrategy;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class JobErrorReportingClientFactoryTest {

  @Test
  void testCreateErrorReportingClientLogging() {
    assertTrue(
        JobErrorReportingClientFactory.getClient(
            JobErrorReportingStrategy.LOGGING, Mockito.mock(Configs.class)) instanceof LoggingJobErrorReportingClient);
  }

  @Test
  void testCreateErrorReportingClientSentry() {
    final Configs configsMock = Mockito.mock(Configs.class);
    Mockito.when(configsMock.getJobErrorReportingSentryDSN()).thenReturn("");

    assertTrue(
        JobErrorReportingClientFactory.getClient(
            JobErrorReportingStrategy.SENTRY, configsMock) instanceof SentryJobErrorReportingClient);
  }

}
