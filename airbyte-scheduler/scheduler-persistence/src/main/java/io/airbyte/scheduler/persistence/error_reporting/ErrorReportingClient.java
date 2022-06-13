package io.airbyte.scheduler.persistence.error_reporting;

import io.airbyte.config.Configs.ErrorReportingStrategy;

// TODO should live in airbyte-analytics, or maybe some other module e.g; airbyte-sentry??
public interface ErrorReportingClient {
  void report();

  static ErrorReportingClient getClient(final ErrorReportingStrategy strategy){
    // TODO
    return null;
  }
}
