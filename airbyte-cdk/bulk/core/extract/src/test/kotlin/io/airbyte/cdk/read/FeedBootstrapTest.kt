/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.IntFieldType
import io.airbyte.cdk.discover.StringFieldType
import io.airbyte.cdk.discover.TestMetaFieldDecorator
import io.airbyte.cdk.discover.TestMetaFieldDecorator.GlobalCursor
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
class FeedBootstrapTest {

    @Inject lateinit var outputConsumer: BufferingOutputConsumer

    @Inject lateinit var metaFieldDecorator: TestMetaFieldDecorator

    val k = Field("k", IntFieldType)
    val v = Field("v", StringFieldType)
    val stream: Stream =
        Stream(
            id = StreamIdentifier.from(StreamDescriptor().withName("tbl").withNamespace("ns")),
            schema =
                setOf(
                    k,
                    v,
                    GlobalCursor,
                    CommonMetaField.CDC_UPDATED_AT,
                    CommonMetaField.CDC_DELETED_AT
                ),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = listOf(k),
            configuredCursor = GlobalCursor,
        )

    val global = Global(listOf(stream))

    fun stateQuerier(
        globalStateValue: OpaqueStateValue? = null,
        streamStateValue: OpaqueStateValue? = null
    ): StateQuerier =
        object : StateQuerier {
            override val feeds: List<Feed> = listOf(global, stream)

            override fun current(feed: Feed): OpaqueStateValue? =
                when (feed) {
                    is Global -> globalStateValue
                    is Stream -> streamStateValue
                }

            override fun resetFeedStates() {
                // no-op
            }
        }

    fun Feed.bootstrap(stateQuerier: StateQuerier): FeedBootstrap<*> =
        FeedBootstrap.create(outputConsumer, metaFieldDecorator, stateQuerier, this)

    fun expected(vararg data: String): List<String> {
        val ts = outputConsumer.recordEmittedAt.toEpochMilli()
        return data.map { """{"namespace":"ns","stream":"tbl","data":$it,"emitted_at":$ts}""" }
    }

    @Test
    fun testGlobalColdStart() {
        val globalBootstrap: FeedBootstrap<*> = global.bootstrap(stateQuerier())
        Assertions.assertNull(globalBootstrap.currentState)
        Assertions.assertEquals(1, globalBootstrap.streamRecordConsumers().size)
        val (actualStreamID, consumer) = globalBootstrap.streamRecordConsumers().toList().first()
        Assertions.assertEquals(stream.id, actualStreamID)
        consumer.accept(Jsons.readTree(GLOBAL_RECORD_DATA) as ObjectNode, changes = null)
        Assertions.assertEquals(
            expected(GLOBAL_RECORD_DATA),
            outputConsumer.records().map(Jsons::writeValueAsString)
        )
    }

    @Test
    fun testGlobalWarmStart() {
        val globalBootstrap: FeedBootstrap<*> =
            global.bootstrap(stateQuerier(globalStateValue = Jsons.objectNode()))
        Assertions.assertEquals(Jsons.objectNode(), globalBootstrap.currentState)
        Assertions.assertEquals(1, globalBootstrap.streamRecordConsumers().size)
        val (actualStreamID, consumer) = globalBootstrap.streamRecordConsumers().toList().first()
        Assertions.assertEquals(stream.id, actualStreamID)
        consumer.accept(Jsons.readTree(GLOBAL_RECORD_DATA) as ObjectNode, changes = null)
        Assertions.assertEquals(
            expected(GLOBAL_RECORD_DATA),
            outputConsumer.records().map(Jsons::writeValueAsString)
        )
    }

    @Test
    fun testStreamColdStart() {
        val streamBootstrap: FeedBootstrap<*> =
            stream.bootstrap(stateQuerier(globalStateValue = Jsons.objectNode()))
        Assertions.assertNull(streamBootstrap.currentState)
        Assertions.assertEquals(1, streamBootstrap.streamRecordConsumers().size)
        val (actualStreamID, consumer) = streamBootstrap.streamRecordConsumers().toList().first()
        Assertions.assertEquals(stream.id, actualStreamID)
        consumer.accept(Jsons.readTree(STREAM_RECORD_INPUT_DATA) as ObjectNode, changes = null)
        Assertions.assertEquals(
            expected(STREAM_RECORD_OUTPUT_DATA),
            outputConsumer.records().map(Jsons::writeValueAsString)
        )
    }

    @Test
    fun testStreamWarmStart() {
        val streamBootstrap: FeedBootstrap<*> =
            stream.bootstrap(
                stateQuerier(
                    globalStateValue = Jsons.objectNode(),
                    streamStateValue = Jsons.arrayNode(),
                )
            )
        Assertions.assertEquals(Jsons.arrayNode(), streamBootstrap.currentState)
        Assertions.assertEquals(1, streamBootstrap.streamRecordConsumers().size)
        val (actualStreamID, consumer) = streamBootstrap.streamRecordConsumers().toList().first()
        Assertions.assertEquals(stream.id, actualStreamID)
        consumer.accept(Jsons.readTree(STREAM_RECORD_INPUT_DATA) as ObjectNode, changes = null)
        Assertions.assertEquals(
            expected(STREAM_RECORD_OUTPUT_DATA),
            outputConsumer.records().map(Jsons::writeValueAsString)
        )
    }

    @Test
    fun testChanges() {
        val stateQuerier =
            object : StateQuerier {
                override val feeds: List<Feed> = listOf(stream)
                override fun current(feed: Feed): OpaqueStateValue? = null
                override fun resetFeedStates() {
                    // no-op
                }
            }
        val streamBootstrap = stream.bootstrap(stateQuerier) as StreamFeedBootstrap
        val consumer: StreamRecordConsumer = streamBootstrap.streamRecordConsumer()
        val changes =
            mapOf(
                k to FieldValueChange.RECORD_SIZE_LIMITATION_TRUNCATION,
                v to FieldValueChange.RETRIEVAL_FAILURE_TOTAL,
            )
        consumer.accept(Jsons.readTree("""{"k":1}""") as ObjectNode, changes)
        Assertions.assertEquals(
            listOf(
                Jsons.writeValueAsString(
                    Jsons.readTree(
                        """{
                |"namespace":"ns",
                |"stream":"tbl",
                |"data":{
                |"k":1,"v":null,
                |"_ab_cdc_lsn":null,"_ab_cdc_updated_at":null,"_ab_cdc_deleted_at":null},
                |"emitted_at":3133641600000,
                |"meta":{"changes":[
                |{"field":"k","change":"TRUNCATED","reason":"SOURCE_RECORD_SIZE_LIMITATION"},
                |{"field":"v","change":"NULLED","reason":"SOURCE_RETRIEVAL_ERROR"}
                |]}}""".trimMargin()
                    )
                )
            ),
            outputConsumer.records().map(Jsons::writeValueAsString)
        )
    }

    companion object {
        const val GLOBAL_RECORD_DATA =
            """{"k":1,"v":"foo","_ab_cdc_lsn":123,"_ab_cdc_updated_at":"2024-03-01T01:02:03.456789","_ab_cdc_deleted_at":null}"""
        const val STREAM_RECORD_INPUT_DATA = """{"k":2,"v":"bar"}"""
        const val STREAM_RECORD_OUTPUT_DATA =
            """{"k":2,"v":"bar","_ab_cdc_lsn":{},"_ab_cdc_updated_at":"2069-04-20T00:00:00.000000Z","_ab_cdc_deleted_at":null}"""
    }
}
