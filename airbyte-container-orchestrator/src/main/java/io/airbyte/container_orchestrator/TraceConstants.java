/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

/**
 * Collection of constants for APM tracing.
 */
public class TraceConstants {

  public static final String JOB_ORCHESTRATOR_OPERATION_NAME = "job.orchestrator";

  private TraceConstants() {}

  /**
   * Trace tag constants.
   */
  public static final class Tags {

    /**
     * Name of the APM trace tag that holds the destination Docker image value associated with the
     * trace.
     */
    public static final String DESTINATION_DOCKER_IMAGE_KEY = "destination.docker_image";

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
