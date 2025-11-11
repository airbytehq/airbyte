/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.process

/**
 * The following variables help, either via names or labels, add metadata to processes actually
 * running operations to ease operations.
 */
object Metadata {
    /** General Metadata */
    const val JOB_LABEL_KEY: String = "job_id"
    const val ATTEMPT_LABEL_KEY: String = "attempt_id"
    const val WORKER_POD_LABEL_KEY: String = "airbyte"
    const val WORKER_POD_LABEL_VALUE: String = "job-pod"
    const val CONNECTION_ID_LABEL_KEY: String = "connection_id"

    /** These are more readable forms of [io.airbyte.config.JobTypeResourceLimit.JobType]. */
    const val JOB_TYPE_KEY: String = "job_type"
    const val SYNC_JOB: String = "sync"
    const val SPEC_JOB: String = "spec"
    const val CHECK_JOB: String = "check"
    const val DISCOVER_JOB: String = "discover"

    /**
     * A sync job can actually be broken down into the following steps. Try to be as precise as
     * possible with naming/labels to help operations.
     */
    const val SYNC_STEP_KEY: String = "sync_step"
    const val READ_STEP: String = "read"
    const val WRITE_STEP: String = "write"
    const val NORMALIZE_STEP: String = "normalize"
    const val CUSTOM_STEP: String = "custom"
    const val ORCHESTRATOR_STEP: String = "orchestrator"
}
