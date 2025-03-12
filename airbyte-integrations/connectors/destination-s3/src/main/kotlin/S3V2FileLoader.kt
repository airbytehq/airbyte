package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.write.object_storage.FileLoader
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Singleton

@Singleton
@Requires(property = "airbyte.destination.core.file-transfer.enabled", value = "true")
class S3V2FileLoader(
    config: S3V2Configuration<*>
): FileLoader, ObjectLoader {
    override val numPartWorkers: Int = config.numPartWorkers
    override val numUploadWorkers: Int = config.numUploadWorkers
    override val partSizeBytes: Long = config.partSizeBytes
    override val maxMemoryRatioReservedForParts: Double = config.maxMemoryRatioReservedForParts
}
