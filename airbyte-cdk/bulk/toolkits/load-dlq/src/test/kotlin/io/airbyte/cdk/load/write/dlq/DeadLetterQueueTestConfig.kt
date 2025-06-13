/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.dlq

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageSpec
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider
import io.airbyte.cdk.load.command.dlq.ObjectStorageSpec
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.LoadPipeline
import jakarta.inject.Singleton

class DeadLetterQueueTestAggregator : AutoCloseable {
    override fun close() {
        TODO("Not yet implemented")
    }
}

class DeadLetterQueueTestLoader : DlqLoader<DeadLetterQueueTestAggregator> {
    override fun start(key: StreamKey, part: Int): DeadLetterQueueTestAggregator {
        TODO("Not yet implemented")
    }

    override fun close() {
        TODO("Not yet implemented")
    }

    override fun finish(state: DeadLetterQueueTestAggregator): DlqLoader.Complete {
        TODO("Not yet implemented")
    }

    override fun accept(
        record: DestinationRecordRaw,
        state: DeadLetterQueueTestAggregator
    ): DlqLoader.DlqLoadResult {
        TODO("Not yet implemented")
    }
}

@Singleton
class DeadLetterQueueTestSpecification : ConfigurationSpecification() {
    val objectStorageConfig: ObjectStorageSpec = DisabledObjectStorageSpec()
}

@Singleton
class DeadLetterQueueTestConfigurationFactory :
    DestinationConfigurationFactory<
        DeadLetterQueueTestSpecification, DeadLetterQueueTestConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: DeadLetterQueueTestSpecification
    ): DeadLetterQueueTestConfiguration =
        DeadLetterQueueTestConfiguration(
            objectStorageConfig = pojo.objectStorageConfig.toObjectStorageConfig(),
        )
}

data class DeadLetterQueueTestConfiguration(
    override val objectStorageConfig: ObjectStorageConfig,
) : DestinationConfiguration(), ObjectStorageConfigProvider

@Singleton
fun loadPipeline(
    dlqPipelineFactory: DlqPipelineFactory,
): LoadPipeline = dlqPipelineFactory.createPipeline(DeadLetterQueueTestLoader())
