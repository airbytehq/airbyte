/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.integrationTest

import DlqStateWithRecordSample
import DlqStateWithSampleAndEmptyList
import io.airbyte.cdk.load.MockObjectStorageClient
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.dlq.ConfigurationSpecificationWithDlq
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.dlq.DlqLoader
import io.airbyte.cdk.load.write.dlq.DlqPipelineFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

const val DLQ_INTEGRATION_TEST_ENV = "dlq-integration-test"
const val DLQ_SAMPLE_TEST = "dlq-sample-test"
const val DLQ_SAMPLE_WITH_EMPTY_LIST_TEST = "dlq-sample-with-empty-list-test"

class DlqTestSpec : ConfigurationSpecificationWithDlq()

class DlqTestConfig(override val objectStorageConfig: ObjectStorageConfig) :
    DestinationConfiguration(), ObjectStorageConfigProvider

class DlqTestStreamLoader(override val stream: DestinationStream) : StreamLoader

interface DlqTestState : AutoCloseable {
    fun accumulate(record: DestinationRecordRaw)

    fun isFull(): Boolean

    fun flush(): List<DestinationRecordRaw>?
}

interface DlqStateFactory {
    fun create(key: StreamKey, part: Int): DlqTestState
}

class DlqTestLoader(private val stateFactory: DlqStateFactory) : DlqLoader<DlqTestState> {
    override fun start(key: StreamKey, part: Int): DlqTestState = stateFactory.create(key, part)

    override fun close() {}

    override fun finish(state: DlqTestState): DlqLoader.Complete = DlqLoader.Complete(state.flush())

    override fun accept(
        record: DestinationRecordRaw,
        state: DlqTestState
    ): DlqLoader.DlqLoadResult {
        state.accumulate(record)
        return if (state.isFull()) DlqLoader.Complete(state.flush()) else DlqLoader.Incomplete
    }
}

@Factory
@Requires(env = [DLQ_INTEGRATION_TEST_ENV])
class DlqTestFactory {
    @Singleton fun spec() = DlqTestSpec()

    @Singleton
    fun specExtension() =
        object : DestinationSpecificationExtension {
            override val supportedSyncModes = listOf(DestinationSyncMode.APPEND)
            override val supportsIncremental = true
        }

    @Singleton
    fun configurationFactory() =
        object : DestinationConfigurationFactory<DlqTestSpec, DlqTestConfig> {
            override fun makeWithoutExceptionHandling(pojo: DlqTestSpec): DlqTestConfig =
                DlqTestConfig(
                    objectStorageConfig = pojo.objectStorageConfig.toObjectStorageConfig()
                )
        }

    @Singleton
    fun objectLoader() =
        object : ObjectLoader {
            override val inputPartitions = 1
            override val numPartWorkers = 1
        }

    @Singleton
    fun checker(dlqChecker: DlqChecker) =
        object : DestinationChecker<DlqTestConfig> {
            override fun check(config: DlqTestConfig) {
                dlqChecker.check(config.objectStorageConfig)
            }
        }

    @Singleton
    fun writer() =
        object : DestinationWriter {
            override fun createStreamLoader(stream: DestinationStream): StreamLoader {
                return DlqTestStreamLoader(stream)
            }
        }

    @Singleton
    fun loadPipeline(
        catalog: DestinationCatalog,
        dlqPipelineFactory: DlqPipelineFactory,
        dlqStateFactory: DlqStateFactory,
    ): LoadPipeline = dlqPipelineFactory.createPipeline(DlqTestLoader(dlqStateFactory))

    @Singleton
    @Secondary
    fun dlqStateFromRecordSampleFactory(): DlqStateFactory = DlqStateWithRecordSample.Factory()

    @Singleton
    @Requires(env = [DLQ_SAMPLE_WITH_EMPTY_LIST_TEST])
    fun dlqStateFromRecordSampleWithEmptyListFactory(): DlqStateFactory =
        DlqStateWithSampleAndEmptyList.Factory()

    @Singleton
    @Requires(env = [DLQ_SAMPLE_TEST])
    fun dlqStateFromNewRecordFactory(): DlqStateFactory = DlqStateWithNewRecords.Factory()

    @Singleton
    @Requires(env = ["MockObjectStorage"])
    fun objectClient(): ObjectStorageClient<*> = MockObjectStorageClient()
}
