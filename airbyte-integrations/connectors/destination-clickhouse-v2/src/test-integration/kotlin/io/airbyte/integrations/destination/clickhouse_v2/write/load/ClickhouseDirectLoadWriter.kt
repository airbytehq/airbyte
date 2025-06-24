/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.load

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.ClientFaultCause
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseConfigUpdater
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseContainerHelper
import io.airbyte.integrations.destination.clickhouse_v2.Utils
import io.airbyte.integrations.destination.clickhouse_v2.fixtures.ClickhouseExpectedRecordMapper
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecificationOss
import io.airbyte.integrations.destination.clickhouse_v2.write.load.ClientProvider.getClient
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.time.ZonedDateTime
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled

class ClickhouseDirectLoadWriter :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Utils.getConfigPath("valid_connection.json")),
        configSpecClass = ClickhouseSpecificationOss::class.java,
        dataDumper =
            ClickhouseDataDumper { spec ->
                val configOverrides = mutableMapOf<String, String>()
                ClickhouseConfigurationFactory()
                    .makeWithOverrides(spec as ClickhouseSpecificationOss, configOverrides)
            },
        destinationCleaner = ClickhouseDataCleaner,
        recordMangler = ClickhouseExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.SOFT_DELETE),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        unionBehavior = UnionBehavior.STRICT_STRINGIFY,
        preserveUndeclaredFields = false,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = true,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = false,
                nestedFloatLosesPrecision = false,
            ),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
        configUpdater = ClickhouseConfigUpdater(),
        dedupChangeUsesDefault = true,
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            ClickhouseContainerHelper.start()
        }

        @JvmStatic
        @BeforeAll
        fun afterAll() {
            ClickhouseContainerHelper.stop()
        }
    }

    @Disabled("Clickhouse does not support file transfer, so this test is skipped.")
    override fun testBasicWriteFile() {
        // Clickhouse does not support file transfer, so this test is skipped.
    }

    /**
     * failing because of
     *
     * java.lang.ClassCastException: class com.fasterxml.jackson.databind.node.NullNode cannot be
     * cast to class com.fasterxml.jackson.databind.node.ObjectNode
     * (com.fasterxml.jackson.databind.node.NullNode and
     * com.fasterxml.jackson.databind.node.ObjectNode are in unnamed module of loader 'app') at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.accept(ClickhouseDirectLoader.kt:51)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.accept(DirectLoadRecordAccumulator.kt:37)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.accept(DirectLoadRecordAccumulator.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask$execute$$inlined$fold$1.emit(Reduce.kt:225)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.emitAllImpl$FlowKt__ChannelsKt(Channels.kt:33)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.access$emitAllImpl$FlowKt__ChannelsKt(Channels.kt:1)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt$emitAllImpl$1.invokeSuspend(Channels.kt)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:33)
     * ~[kotlin-stdlib-2.1.10.jar:2.1.10-release-473] at
     * kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:101)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:113)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:89)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:589)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:823)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:720)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:707)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?]
     */
    @Disabled override fun testFunkyCharacters() {}

    @Disabled override fun testNoColumns() {}

    /** Dedup is handle by the Clickhouse server, so this test is not applicable. */
    @Disabled override fun testFunkyCharactersDedup() {}
}

class ClickhouseDataDumper(
    private val configProvider: (ConfigurationSpecification) -> ClickhouseConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val client = getClient(config)

        val isDedup = stream.importType is Dedupe

        val output = mutableListOf<OutputRecord>()

        val namespacedTableName =
            "${stream.mappedDescriptor.namespace ?: config.resolvedDatabase}.${stream.mappedDescriptor.name}"

        val response =
            client.query("SELECT * FROM $namespacedTableName ${if (isDedup) "FINAL" else ""}").get()

        val schema = client.getTableSchema(namespacedTableName)

        val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response, schema)
        while (reader.hasNext()) {
            val record = reader.next()
            val dataMap = linkedMapOf<String, AirbyteValue>()
            record.entries
                .filter { entry -> !Meta.COLUMN_NAMES.contains(entry.key) }
                .forEach { entry -> dataMap[entry.key] = AirbyteValue.from(entry.value) }
            val outputRecord =
                OutputRecord(
                    rawId = record[Meta.COLUMN_NAME_AB_RAW_ID] as String,
                    extractedAt =
                        (record[Meta.COLUMN_NAME_AB_EXTRACTED_AT] as ZonedDateTime)
                            .toInstant()
                            .toEpochMilli(),
                    loadedAt = null,
                    generationId = record[Meta.COLUMN_NAME_AB_GENERATION_ID] as Long,
                    data = ObjectValue(dataMap),
                    airbyteMeta = stringToMeta(record[Meta.COLUMN_NAME_AB_META] as String),
                )
            output.add(outputRecord)
        }

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("Clickhouse does not support file transfer.")
    }
}

object ClickhouseDataCleaner : DestinationCleaner {
    private val clickhouseSpecification =
        ValidatedJsonUtils.parseOne(
            ClickhouseSpecificationOss::class.java,
            Files.readString(Utils.getConfigPath("valid_connection.json"))
        )

    private val config =
        ClickhouseConfigurationFactory()
            .makeWithOverrides(
                clickhouseSpecification,
                mapOf(
                    "hostname" to ClickhouseContainerHelper.getIpAddress()!!,
                    "port" to (ClickhouseContainerHelper.getPort()?.toString())!!,
                    "protocol" to "http",
                    "username" to ClickhouseContainerHelper.getUsername()!!,
                    "password" to ClickhouseContainerHelper.getPassword()!!,
                )
            )

    override fun cleanup() {
        try {
            val client = getClient(config)

            val query = "select * from system.databases where name like 'test%'"

            val response = client.query(query).get()

            val reader = client.newBinaryFormatReader(response)
            while (reader.hasNext()) {
                val record = reader.next()
                val databaseName = record["name"] as String

                client.query("DROP DATABASE IF EXISTS $databaseName").get()
            }
        } catch (e: Exception) {
            // swallow the exception, we don't want to fail the test suite if the cleanup fails
        }
    }
}

fun stringToMeta(metaAsString: String): OutputRecord.Meta {
    if (metaAsString.isEmpty()) {
        return OutputRecord.Meta(
            changes = emptyList(),
            syncId = null,
        )
    }
    val metaJson = Jsons.readTree(metaAsString)

    val changes =
        (metaJson["changes"] as ArrayNode).map { change ->
            Meta.Change(
                field = change["field"].textValue(),
                change =
                    AirbyteRecordMessageMetaChange.Change.fromValue(change["change"].textValue()),
                reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(change["reason"].textValue()),
            )
        }

    return OutputRecord.Meta(
        changes = changes,
        syncId = metaJson["sync_id"].longValue(),
    )
}

object ClientProvider {
    fun getClient(config: ClickhouseConfiguration): Client {
        return Client.Builder()
            .setPassword(config.password)
            .setUsername(config.username)
            .addEndpoint(config.endpoint)
            .setDefaultDatabase(config.resolvedDatabase)
            .retryOnFailures(ClientFaultCause.None)
            .build()
    }
}
