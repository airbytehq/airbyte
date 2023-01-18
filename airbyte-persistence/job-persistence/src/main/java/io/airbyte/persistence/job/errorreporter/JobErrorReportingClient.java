/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.errorreporter;

import edu.umd.cs.findbugs.annotations.Nullable;
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
  void reportJobFailureReason(@Nullable StandardWorkspace workspace,
                              final FailureReason reason,
                              @Nullable final String dockerImage,
                              Map<String, String> metadata);

}
