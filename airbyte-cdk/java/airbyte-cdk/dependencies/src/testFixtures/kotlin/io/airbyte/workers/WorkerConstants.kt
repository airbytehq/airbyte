/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers

object WorkerConstants {
    const val SOURCE_CONFIG_JSON_FILENAME: String = "source_config.json"
    const val DESTINATION_CONFIG_JSON_FILENAME: String = "destination_config.json"

    const val SOURCE_CATALOG_JSON_FILENAME: String = "source_catalog.json"
    const val DESTINATION_CATALOG_JSON_FILENAME: String = "destination_catalog.json"
    const val INPUT_STATE_JSON_FILENAME: String = "input_state.json"

    const val RESET_JOB_SOURCE_DOCKER_IMAGE_STUB: String = "airbyte_empty"

    const val WORKER_ENVIRONMENT: String = "WORKER_ENVIRONMENT"
}
