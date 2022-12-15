/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

public class WorkerConstants {

  public static final String SOURCE_CONFIG_JSON_FILENAME = "source_config.json";
  public static final String DESTINATION_CONFIG_JSON_FILENAME = "destination_config.json";

  public static final String SOURCE_CATALOG_JSON_FILENAME = "source_catalog.json";
  public static final String DESTINATION_CATALOG_JSON_FILENAME = "destination_catalog.json";
  public static final String INPUT_STATE_JSON_FILENAME = "input_state.json";

  public static final String RESET_JOB_SOURCE_DOCKER_IMAGE_STUB = "airbyte_empty";

  public static final String WORKER_ENVIRONMENT = "WORKER_ENVIRONMENT";

}
