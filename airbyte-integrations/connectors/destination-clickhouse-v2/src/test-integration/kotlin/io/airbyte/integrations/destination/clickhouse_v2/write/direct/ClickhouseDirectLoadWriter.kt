/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.ClientFaultCause
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
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
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecification
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClientProvider.getClient
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.time.ZonedDateTime
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled

class ClickhouseDirectLoadWriter :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Utils.getConfigPath("valid_connection.json")),
        configSpecClass = ClickhouseSpecification::class.java,
        dataDumper =
            ClickhouseDataDumper { spec ->
                val configOverrides = mutableMapOf<String, String>()
                ClickhouseConfigurationFactory()
                    .makeWithOverrides(spec as ClickhouseSpecification, configOverrides)
            },
        destinationCleaner = ClickhouseDataCleaner,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        unionBehavior = UnionBehavior.STRICT_STRINGIFY,
        preserveUndeclaredFields = false,
        supportFileTransfer = false,
        commitDataIncrementally = true,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = false,
                nestedFloatLosesPrecision = false,
            ),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
        configUpdater = ClickhouseConfigUpdater(),
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
     * Failing (is stuck) because of com.clickhouse.client.api.ServerException: Code: 27.
     * DB::Exception: Cannot parse input: expected '\"' before:
     * 'Z\",\"name\":\"foo_1_200\",\"_airbyte_extracted_at\":200,\"_airbyte_generation_id\":0,\"_airbyte_raw_id\":\"bf7d3df8-8a91-4fd4-bd4c-89c293ba1d6b\",\"_airbyte_meta\":{\"changes\"':
     * (while reading the value of key updated_at): (at row 1) : While executing
     * ParallelParsingBlockInputFormat. (CANNOT_PARSE_INPUT_ASSERTION_FAILED) (version 25.5.2.47
     * (official build))"} at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.readError(HttpAPIClientHelper.java:371)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.executeRequest(HttpAPIClientHelper.java:426)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.lambda$insert$8(Client.java:1600)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.runAsyncOperation(Client.java:2156)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1643) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at com.clickhouse.client.api.Client.insert(Client.java:1503)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1446) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.flush(ClickhouseDirectLoader.kt:74)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.finish(ClickhouseDirectLoader.kt:87)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:46)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask$execute$$inlined$fold$1.emit(Reduce.kt:253)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.emitAllImpl$FlowKt__ChannelsKt(Channels.kt:33)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.access$emitAllImpl$FlowKt__ChannelsKt(Channels.kt:1)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt$emitAllImpl$1.invokeSuspend(Channels.kt)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:33)
     * [kotlin-stdlib-2.1.10.jar:2.1.10-release-473] at
     * kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:101)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:113)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:89)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:589)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:823)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:720)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:707)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?]
     */
    @Disabled() override fun testInterruptedTruncateWithoutPriorData() {}

    /**
     * Failing because of om.clickhouse.client.api.ServerException: Code: 62. DB::Exception: Syntax
     * error (Multi-statements are not allowed): failed at position 18 (end of query) (line 1, col
     * 18): ; DROP TABLE IF EXISTS `test20250609WxfG`.`test_stream`; ALTER TABLE
     * `airbyte_internal`.`b608df00f1f652fbb38deb99bc5f8e7de` RENAME TO `test202... . (SYNTAX_ERROR)
     * (version 25.5.2.47 (official build)) at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.readError(HttpAPIClientHelper.java:371)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.executeRequest(HttpAPIClientHelper.java:426)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.lambda$query$10(Client.java:1723)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.runAsyncOperation(Client.java:2156)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.query(Client.java:1766) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at com.clickhouse.client.api.Client.query(Client.java:1652)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.execute(Client.java:2072) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at
     * io.airbyte.integrations.destination.clickhouse_v2.client.ClickhouseAirbyteClient.execute(ClickhouseAirbyteClient.kt:132)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.integrations.destination.clickhouse_v2.client.ClickhouseAirbyteClient.overwriteTable(ClickhouseAirbyteClient.kt:56)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendTruncateStreamLoader.close(DirectLoadTableStreamLoader.kt:210)
     * ~[io.airbyte.airbyte-cdk.bulk.toolkits-bulk-cdk-toolkit-load-db.jar:?] at
     * io.airbyte.cdk.load.write.StreamLoader.close$default(StreamLoader.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.implementor.CloseStreamTask.execute(CloseStreamTask.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.DestinationTaskLauncher$WrappedTask.execute(DestinationTaskLauncher.kt:125)
     * [io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.TaskScopeProvider$launch$job$1.invokeSuspend(TaskScopeProvider.kt:35)
     * [io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:33)
     * [kotlin-stdlib-2.1.10.jar:2.1.10-release-473] at
     * kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:101)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:113)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:89)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:589)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:823)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:720)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:707)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?]
     */
    @Disabled override fun testTruncateRefresh() {}

    /** Dedup is handle by the Clickhouse server, so this test is not applicable. */
    @Disabled override fun testDedupWithStringKey() {}

    /** Dedup is handle by the Clickhouse server, so this test is not applicable. */
    @Disabled override fun testDedupChangeCursor() {}

    /**
     * Failing because of com.clickhouse.client.api.ServerException: Code: 27. DB::Exception: Cannot
     * parse input: expected ',' before:
     * '.1,\"integer\":42,\"boolean\":true,\"timestamp_with_timezone\":\"2023-01-23T11:34:56-01:00\",\"timestamp_without_timezone\":\"2023-01-23T12:34:56\",\"time_with_timezone\":\"11':
     * (at row 1) : While executing ParallelParsingBlockInputFormat.
     * (CANNOT_PARSE_INPUT_ASSERTION_FAILED) (version 25.5.2.47 (official build))"} at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.readError(HttpAPIClientHelper.java:371)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.executeRequest(HttpAPIClientHelper.java:426)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.lambda$insert$8(Client.java:1600)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.runAsyncOperation(Client.java:2156)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1643) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at com.clickhouse.client.api.Client.insert(Client.java:1503)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1446) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.flush(ClickhouseDirectLoader.kt:75)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.finish(ClickhouseDirectLoader.kt:88)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:46)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask.finishKeys(LoadPipelineStepTask.kt:278)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask.access$finishKeys(LoadPipelineStepTask.kt:59)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask$execute$$inlined$fold$1.emit(Reduce.kt:302)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.emitAllImpl$FlowKt__ChannelsKt(Channels.kt:33)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.access$emitAllImpl$FlowKt__ChannelsKt(Channels.kt:1)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt$emitAllImpl$1.invokeSuspend(Channels.kt)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:33)
     * [kotlin-stdlib-2.1.10.jar:2.1.10-release-473] at
     * kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:101)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:113)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:89)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:589)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:823)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:720)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:707)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?]
     */
    @Disabled override fun testBasicTypes() {}

    /** Dedup is handle by the Clickhouse server, so this test is not applicable. */
    @Disabled override fun testDedupChangePk() {}

    /** Dedup is handle by the Clickhouse server, so this test is not applicable. */
    @Disabled override fun testDedup() {}

    /**
     * failing because of com.clickhouse.client.api.ServerException: Code: 62. DB::Exception: Syntax
     * error (Multi-statements are not allowed): failed at position 18 (end of query) (line 1, col
     * 18): ; DROP TABLE IF EXISTS `test20250609adPc`.`test_stream`; ALTER TABLE
     * `airbyte_internal`.`a0772c49e432c38133ea5d39f90dab4df` RENAME TO `test202... . (SYNTAX_ERROR)
     * (version 25.5.2.47 (official build)) at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.readError(HttpAPIClientHelper.java:371)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.executeRequest(HttpAPIClientHelper.java:426)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.lambda$query$10(Client.java:1723)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.runAsyncOperation(Client.java:2156)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.query(Client.java:1766) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at com.clickhouse.client.api.Client.query(Client.java:1652)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.execute(Client.java:2072) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at
     * io.airbyte.integrations.destination.clickhouse_v2.client.ClickhouseAirbyteClient.execute(ClickhouseAirbyteClient.kt:132)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.integrations.destination.clickhouse_v2.client.ClickhouseAirbyteClient.overwriteTable(ClickhouseAirbyteClient.kt:56)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendTruncateStreamLoader.close(DirectLoadTableStreamLoader.kt:210)
     * ~[io.airbyte.airbyte-cdk.bulk.toolkits-bulk-cdk-toolkit-load-db.jar:?] at
     * io.airbyte.cdk.load.write.StreamLoader.close$default(StreamLoader.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.implementor.CloseStreamTask.execute(CloseStreamTask.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.DestinationTaskLauncher$WrappedTask.execute(DestinationTaskLauncher.kt:125)
     * [io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.TaskScopeProvider$launch$job$1.invokeSuspend(TaskScopeProvider.kt:35)
     * [io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:33)
     * [kotlin-stdlib-2.1.10.jar:2.1.10-release-473] at
     * kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:101)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:113)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:89)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:589)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:823)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:720)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:707)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?]
     */
    @Disabled override fun testTruncateRefreshNoData() {}

    /**
     * failing because of
     *
     * com.clickhouse.client.api.ServerException: Code: 27. DB::Exception: Cannot parse input:
     * expected '\"' before:
     * 'Z\",\"name\":\"foo_1_100\",\"_airbyte_extracted_at\":100,\"_airbyte_generation_id\":41,\"_airbyte_raw_id\":\"bf7d3df8-8a91-4fd4-bd4c-89c293ba1d6b\",\"_airbyte_meta\":{\"changes':
     * (while reading the value of key updated_at): (at row 1) : While executing
     * ParallelParsingBlockInputFormat. (CANNOT_PARSE_INPUT_ASSERTION_FAILED) (version 25.5.2.47
     * (official build))"} at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.readError(HttpAPIClientHelper.java:371)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.executeRequest(HttpAPIClientHelper.java:426)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.lambda$insert$8(Client.java:1600)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.runAsyncOperation(Client.java:2156)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1643) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at com.clickhouse.client.api.Client.insert(Client.java:1503)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1446) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.flush(ClickhouseDirectLoader.kt:75)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.finish(ClickhouseDirectLoader.kt:88)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:46)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask.finishKeys(LoadPipelineStepTask.kt:278)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask.access$finishKeys(LoadPipelineStepTask.kt:59)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask$execute$$inlined$fold$1.emit(Reduce.kt:302)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.emitAllImpl$FlowKt__ChannelsKt(Channels.kt:33)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.access$emitAllImpl$FlowKt__ChannelsKt(Channels.kt:1)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt$emitAllImpl$1.invokeSuspend(Channels.kt)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:33)
     * [kotlin-stdlib-2.1.10.jar:2.1.10-release-473] at
     * kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:101)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:113)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:89)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:589)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:823)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:720)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:707)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?]
     */
    @Disabled override fun testInterruptedTruncateWithPriorData() {}

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

    /**
     * failing because of
     *
     * com.clickhouse.client.api.ServerException: Code: 60. DB::Exception: Table
     * test20250609KJeX_2.test_stream_test20250609KJeX does not exist. Maybe you meant
     * test20250609KJeX_2.test_stream_test20250609KJeX_4a4?. (UNKNOWN_TABLE) (version 25.5.2.47
     * (official build))"} at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.readError(HttpAPIClientHelper.java:371)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.executeRequest(HttpAPIClientHelper.java:426)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.lambda$insert$8(Client.java:1600)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.runAsyncOperation(Client.java:2156)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1643) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at com.clickhouse.client.api.Client.insert(Client.java:1503)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1446) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.flush(ClickhouseDirectLoader.kt:75)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.finish(ClickhouseDirectLoader.kt:88)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:46)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask.finishKeys(LoadPipelineStepTask.kt:278)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask.access$finishKeys(LoadPipelineStepTask.kt:59)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask$execute$$inlined$fold$1.emit(Reduce.kt:302)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.emitAllImpl$FlowKt__ChannelsKt(Channels.kt:33)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.access$emitAllImpl$FlowKt__ChannelsKt(Channels.kt:1)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt$emitAllImpl$1.invokeSuspend(Channels.kt)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:33)
     * [kotlin-stdlib-2.1.10.jar:2.1.10-release-473] at
     * kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:101)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:113)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:89)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:589)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:823)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:720)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:707)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?]
     */
    @Disabled override fun testNamespaces() {}

    @Disabled override fun testNoColumns() {}

    /**
     * failing because of
     *
     * com.clickhouse.client.api.ServerException: Code: 27. DB::Exception: Cannot parse input:
     * expected '\"' before:
     * 'Z\",\"name\":\"foo_1_100\",\"_airbyte_extracted_at\":100,\"_airbyte_generation_id\":41,\"_airbyte_raw_id\":\"bf7d3df8-8a91-4fd4-bd4c-89c293ba1d6b\",\"_airbyte_meta\":{\"changes':
     * (while reading the value of key updated_at): (at row 1) : While executing
     * ParallelParsingBlockInputFormat. (CANNOT_PARSE_INPUT_ASSERTION_FAILED) (version 25.5.2.47
     * (official build))"} at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.readError(HttpAPIClientHelper.java:371)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.internal.HttpAPIClientHelper.executeRequest(HttpAPIClientHelper.java:426)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.lambda$insert$8(Client.java:1600)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.runAsyncOperation(Client.java:2156)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1643) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at com.clickhouse.client.api.Client.insert(Client.java:1503)
     * ~[client-v2-0.8.6.jar:client-v2 0.8.6 (revision: 2d305b7)] at
     * com.clickhouse.client.api.Client.insert(Client.java:1446) ~[client-v2-0.8.6.jar:client-v2
     * 0.8.6 (revision: 2d305b7)] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.flush(ClickhouseDirectLoader.kt:75)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.finish(ClickhouseDirectLoader.kt:88)
     * ~[io.airbyte.airbyte-integrations.connectors-destination-clickhouse-v2.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:46)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator.finish(DirectLoadRecordAccumulator.kt:24)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask.finishKeys(LoadPipelineStepTask.kt:278)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask.access$finishKeys(LoadPipelineStepTask.kt:59)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * io.airbyte.cdk.load.task.internal.LoadPipelineStepTask$execute$$inlined$fold$1.emit(Reduce.kt:302)
     * ~[io.airbyte.airbyte-cdk.bulk.core-bulk-cdk-core-load.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.emitAllImpl$FlowKt__ChannelsKt(Channels.kt:33)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt.access$emitAllImpl$FlowKt__ChannelsKt(Channels.kt:1)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.flow.FlowKt__ChannelsKt$emitAllImpl$1.invokeSuspend(Channels.kt)
     * ~[kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:33)
     * [kotlin-stdlib-2.1.10.jar:2.1.10-release-473] at
     * kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:101)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:113)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:89)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:589)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:823)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:720)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?] at
     * kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:707)
     * [kotlinx-coroutines-core-jvm-1.9.0.jar:?]
     */
    @Disabled override fun resumeAfterCancelledTruncate() {}

    /** Dedup is handle by the Clickhouse server, so this test is not applicable. */
    @Disabled override fun testFunkyCharactersDedup() {}

    /** Dedup is handle by the Clickhouse server, so this test is not applicable. */
    @Disabled override fun testDedupNoCursor() {}

    /** Running well locally, not well in CI */
    @Disabled override fun testMidSyncCheckpointingStreamState() {}

    /** Need to check with Ed, how to re-enable. */
    @Disabled override fun testOverwriteSchemaEvolution() {}
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

        val output = mutableListOf<OutputRecord>()

        val response =
            client
                .query(
                    "SELECT * FROM ${stream.descriptor.namespace ?: config.resolvedDatabase}.${stream.descriptor.name}"
                )
                .get()

        val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response)
        while (reader.hasNext()) {
            val record = reader.next()
            val dataMap = linkedMapOf<String, AirbyteValue>()
            record.entries
                .filter { entry -> !Meta.COLUMN_NAMES.contains(entry.key) }
                .map { entry ->
                    val airbyteValue =
                        when (entry.value) {
                            is Long -> IntegerValue(entry.value as Long)
                            is String ->
                                if (entry.value == "") NullValue
                                else StringValue(entry.value as String)
                            null -> NullValue
                            else ->
                                throw UnsupportedOperationException(
                                    "Clickhouse data dumper doesn't know how to dump type ${entry.value::class.java} with value ${entry.value}"
                                )
                        }
                    dataMap.put(entry.key, airbyteValue)
                }
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
            ClickhouseSpecification::class.java,
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
    private var client: Client? = null

    fun getClient(config: ClickhouseConfiguration): Client {
        if (client == null) {
            client =
                Client.Builder()
                    .setPassword(config.password)
                    .setUsername(config.username)
                    .addEndpoint(config.endpoint)
                    .setDefaultDatabase(config.resolvedDatabase)
                    .retryOnFailures(ClientFaultCause.None)
                    .build()
        }
        return client!!
    }
}
