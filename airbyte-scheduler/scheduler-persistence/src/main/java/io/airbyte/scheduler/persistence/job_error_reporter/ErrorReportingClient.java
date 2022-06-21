/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.config.Configs.ErrorReportingStrategy;
import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardWorkspace;
import java.util.Map;

// TODO should live in airbyte-analytics, or maybe some other module e.g; airbyte-error-reporting?
public interface ErrorReportingClient {

  void report(StandardWorkspace workspace, final FailureReason reason, final String dockerImage, Map<String, String> metadata);

  static ErrorReportingClient getClient(final ErrorReportingStrategy strategy) {
    // TODO
    return new SentryErrorReportingClient();
    // return new LoggingErrorReportingClient();
  }

}
