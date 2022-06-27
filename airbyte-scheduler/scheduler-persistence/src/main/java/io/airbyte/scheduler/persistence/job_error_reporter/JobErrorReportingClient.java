/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardWorkspace;
import java.util.Map;

/**
 * A generic interface for a client that reports errors
 */
public interface JobErrorReportingClient {

  /**
   * Report a job failure reason
   */
  void reportJobFailureReason(StandardWorkspace workspace, final FailureReason reason, final String dockerImage, Map<String, String> metadata);

}
