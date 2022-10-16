/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

/**
 * These extra env variables are created on the fly and passed to the connector.
 */
public class WorkerEnvConstants {

  public static final String WORKER_CONNECTOR_IMAGE = "WORKER_CONNECTOR_IMAGE";
  public static final String WORKER_JOB_ID = "WORKER_JOB_ID";
  public static final String WORKER_JOB_ATTEMPT = "WORKER_JOB_ATTEMPT";

}
