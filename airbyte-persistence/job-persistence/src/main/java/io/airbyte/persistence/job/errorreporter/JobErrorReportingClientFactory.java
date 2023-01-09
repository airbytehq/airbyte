/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.errorreporter;

import io.airbyte.config.Configs;
import io.airbyte.config.Configs.JobErrorReportingStrategy;

public class JobErrorReportingClientFactory {

  /**
   * Creates an error reporting client based on the desired strategy to use
   *
   * @param strategy - which type of error reporting client should be created
   * @return JobErrorReportingClient
   */
  public static JobErrorReportingClient getClient(final JobErrorReportingStrategy strategy, final Configs configs) {
    return switch (strategy) {
      case SENTRY -> new SentryJobErrorReportingClient(configs.getJobErrorReportingSentryDSN(), new SentryExceptionHelper());
      case LOGGING -> new LoggingJobErrorReportingClient();
    };
  }

}
