/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.config.Configs.ErrorReportingStrategy;

public class ErrorReportingClientFactory {

  /**
   * Creates an error reporting client based on the desired strategy to use
   *
   * @param strategy - which type of error reporting client should be created
   * @return ErrorReportingClient
   */
  public static ErrorReportingClient getClient(final ErrorReportingStrategy strategy) {
    return switch (strategy) {
      case SENTRY -> new SentryErrorReportingClient();
      case LOGGING -> new LoggingErrorReportingClient();
    };
  }

}
