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

  public static final String CONNECTION_ID = "connection_id";
  public static final String FAILURE_ORIGIN = "failure_origin";
  public static final String JOB_ID = "job_id";
  public static final String JOB_STATUS = "job_status";
  public static final String RELEASE_STAGE = "release_stage";
  public static final String RESET_WORKFLOW_FAILURE_CAUSE = "failure_cause";
  public static final String WORKFLOW_TYPE = "workflow_type";
  public static final String ATTEMPT_QUEUE = "attempt_queue";
  public static final String GEOGRAPHY = "geography";
  public static final String UNKNOWN = "unknown";

  public static String getReleaseStage(final ReleaseStage stage) {
    return stage != null ? stage.getLiteral() : UNKNOWN;
  }

  public static String getFailureOrigin(final FailureOrigin origin) {
    return origin != null ? origin.value() : UNKNOWN;
  }

  public static String getJobStatus(final JobStatus status) {
    return status != null ? status.getLiteral() : UNKNOWN;
  }

}
