/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.trace;

/**
 * Collection of constants for APM tracing of Temporal activities and workflows.
 */
public final class TemporalTraceConstants {

  /**
   * Operation name for an APM trace of a Temporal activity.
   */
  public static final String ACTIVITY_TRACE_OPERATION_NAME = "activity";

  /**
   * Operation name for an APM trace of a Temporal workflow.
   */
  public static final String WORKFLOW_TRACE_OPERATION_NAME = "workflow";

  private TemporalTraceConstants() {}

  /**
   * Trace tag constants.
   */
  public static final class Tags {

    /**
     * Name of the APM trace tag that holds the connection ID value associated with the trace.
     */
    public static final String CONNECTION_ID_KEY = "connection_id";

    /**
     * Name of the APM trace tag that holds the destination Docker image value associated with the
     * trace.
     */
    public static final String DESTINATION_DOCKER_IMAGE_KEY = "destination.docker_image";

    /**
     * Name of the APM trace tag that holds the Docker image value associated with the trace.
     */
    public static final String DOCKER_IMAGE_KEY = "docker_image";

    /**
     * Name of the APM trace tag that holds the job ID value associated with the trace.
     */
    public static final String JOB_ID_KEY = "job_id";

    /**
     * Name of the APM trace tag that holds the source Docker image value associated with the trace.
     */
    public static final String SOURCE_DOCKER_IMAGE_KEY = "source.docker_image";

    private Tags() {}

  }

}
