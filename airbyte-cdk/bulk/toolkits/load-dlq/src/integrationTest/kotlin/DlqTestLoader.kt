/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.integrationTest

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.MockObjectStorageClient
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageSpec
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider
import io.airbyte.cdk.load.command.dlq.ObjectStorageSpec
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.IntegerType
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
import jakarta.inject.Singleton
import java.math.BigInteger

class DlqTestSpec : ConfigurationSpecification() {
    val objectStorageConfig: ObjectStorageSpec = DisabledObjectStorageSpec()
}

class DlqTestConfig(override val objectStorageConfig: ObjectStorageConfig) :
    DestinationConfiguration(), ObjectStorageConfigProvider

class DlqTestStreamLoader(override val stream: DestinationStream) : StreamLoader

class DlqTestState : AutoCloseable {
    private val records: MutableList<DestinationRecordRaw> = mutableListOf()

    fun accumulate(record: DestinationRecordRaw) = records.add(record)

    fun isFull(): Boolean = records.size > 2

    fun flush(): List<DestinationRecordRaw>? = records.filter { it.hasAnEvenId() }.ifEmpty { null }

    override fun close() {}

    // Just so that we do not write everything to the dead letter queue
    // we only write even ids that are less than 10
    private fun DestinationRecordRaw.hasAnEvenId(): Boolean {
        val id =
            this.rawData
                .asAirbyteValueProxy()
                .getInteger(AirbyteValueProxy.FieldAccessor(0, "id", IntegerType))
        return id?.let { it < BigInteger.TEN && it.mod(BigInteger.TWO) == BigInteger.ZERO } ?: true
    }
}

class DlqTestLoader : DlqLoader<DlqTestState> {
    override fun start(key: StreamKey, part: Int): DlqTestState = DlqTestState()

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
    ): LoadPipeline = dlqPipelineFactory.createPipeline(DlqTestLoader())

    @Singleton
    @Requires(env = ["MockObjectStorage"])
    fun objectClient(): ObjectStorageClient<*> = MockObjectStorageClient()
}
