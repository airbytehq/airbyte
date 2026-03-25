/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_onelake

import io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import javax.inject.Singleton
import kotlin.math.min

/**
 * Controls upload parallelism and memory allocation for the OneLake destination.
 *
 * Mirrors the Azure Blob Storage object loader but is bound to [MicrosoftOneLakeConfiguration]
 * so the two connectors remain independently tunable.
 */
@Singleton
@Primary
class MicrosoftOneLakeObjectLoader(
    @Value("\${airbyte.destination.core.file-transfer.enabled}") isLegacyFileTransfer: Boolean,
    config: MicrosoftOneLakeConfiguration<*>
) : ObjectLoader {

    override val numPartWorkers: Int =
        if (isLegacyFileTransfer) 1 else config.numPartWorkers

    override val numUploadWorkers: Int = config.numUploadWorkers

    override val maxMemoryRatioReservedForParts: Double = config.maxMemoryRatioReservedForParts

    override val objectSizeBytes: Long = config.objectSizeBytes

    override val partSizeBytes: Long = config.partSizeBytes

    /**
     * Scale per-socket part size to avoid creating too many small parts.
     * Mirrors the Azure Blob Storage connector's formula.
     */
    override fun socketPartSizeBytes(numberOfSockets: Int): Long =
        min((numberOfSockets * 4), 20) * 1024L * 1024

    override fun socketUploadParallelism(numberOfSockets: Int): Int =
        min((numberOfSockets * 4), 25)
}

@Requires(property = "airbyte.destination.core.file-transfer.enabled", value = "false")
@Singleton
@Primary
class OneLakeRoundRobinInputPartitioner : RoundRobinInputPartitioner()

