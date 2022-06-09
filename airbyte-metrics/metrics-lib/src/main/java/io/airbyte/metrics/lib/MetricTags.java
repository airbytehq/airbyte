/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.db.instance.configs.jooq.generated.enums.ReleaseStage;
import io.airbyte.db.instance.jobs.jooq.generated.enums.JobStatus;

/**
 * Keep track of all metric tags.
 */
public class MetricTags {

  private static final String RELEASE_STAGE = "release_stage";
  private static final String FAILURE_ORIGIN = "failure_origin";
  private static final String JOB_STATUS = "job_status";

  public static String getReleaseStage(final ReleaseStage stage) {
    return tagDelimit(RELEASE_STAGE, stage.getLiteral());
  }

  public static String getFailureOrigin(final FailureOrigin origin) {
    return tagDelimit(FAILURE_ORIGIN, origin.value());
  }

  public static String getJobStatus(final JobStatus status) {
    return tagDelimit(JOB_STATUS, status.getLiteral());
  }

  private static String tagDelimit(final String tagName, final String tagVal) {
    return String.join(":", tagName, tagVal);
  }

}
