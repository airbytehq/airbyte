/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

/**
 * Represents a micronaut property, which has a corresponding entry in micronaut's `application.yml`
 * file, which is populated by an environment variable. Just a pair of the micronaut property name,
 * and that corresponding env var name.
 *
 * For example, this application.yaml:
 * ```yaml
 * airbyte:
 *   destination:
 *     foo-bar: ${FOO_BAR}
 * ```
 *
 * Would be represented as `Property("airbyte.destination.foo-bar", "FOO_BAR")`.
 */
data class Property(val micronautProperty: String, val environmentVariable: String)

object EnvVarConstants {
    val FILE_TRANSFER_ENABLED =
        Property(
            "airbyte.destination.core.file-transfer.enabled",
            "USE_FILE_TRANSFER",
        )
    val RECORD_BATCH_SIZE =
        Property(
            "airbyte.destination.core.record-batch-size-override",
            "AIRBYTE_DESTINATION_RECORD_BATCH_SIZE_OVERRIDE",
        )
}
