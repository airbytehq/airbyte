/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardWorkspace;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggingJobErrorReportingClient implements JobErrorReportingClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggingJobErrorReportingClient.class);

  @Override
  public void reportJobFailureReason(final StandardWorkspace workspace,
                                     final FailureReason reason,
                                     final String dockerImage,
                                     final Map<String, String> metadata) {
    LOGGER.info("Report Job Error -> workspaceId: {}, dockerImage: {}, failureReason: {}, metadata: {}",
        workspace.getWorkspaceId(),
        dockerImage,
        reason,
        metadata);
  }

}
