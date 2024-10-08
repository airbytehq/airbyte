/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.IntFieldType
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class StreamStatusManagerTest {

    val streamIncremental =
        Stream(
            id = StreamIdentifier.from(StreamDescriptor().withName("streamIncremental")),
            fields = listOf(Field("v", IntFieldType)),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = null,
            configuredCursor = null,
        )
    val streamFullRefresh =
        Stream(
            id = StreamIdentifier.from(StreamDescriptor().withName("streamFullRefresh")),
            fields = listOf(Field("v", IntFieldType)),
            configuredSyncMode = ConfiguredSyncMode.FULL_REFRESH,
            configuredPrimaryKey = null,
            configuredCursor = null,
        )

    val allStreams: Set<Stream> = setOf(streamFullRefresh, streamIncremental)

    val global: Global
        get() = Global(listOf(streamIncremental))

    val allFeeds: List<Feed> = listOf(global) + allStreams

    @Test
    fun testNothing() {
        TestCase(allFeeds).runTest {}
    }

    @Test
    fun testRunningStream() {
        val testCase = TestCase(listOf(streamFullRefresh), started = setOf(streamFullRefresh))
        testCase.runTest { it.notifyStarting(streamFullRefresh) }
        // Check that the outcome is the same if we call notifyStarting multiple times.
        testCase.runTest {
            it.notifyStarting(streamFullRefresh)
            it.notifyStarting(streamFullRefresh)
            it.notifyStarting(streamFullRefresh)
        }
    }

    @Test
    fun testRunningAndCompleteStream() {
        val testCase =
            TestCase(
                feeds = listOf(streamFullRefresh),
                started = setOf(streamFullRefresh),
                success = setOf(streamFullRefresh),
            )
        testCase.runTest {
            it.notifyStarting(streamFullRefresh)
            it.notifyComplete(streamFullRefresh)
        }
        // Check that the outcome is the same if we forget to call notifyStarting.
        testCase.runTest { it.notifyComplete(streamFullRefresh) }
        // Check that the outcome is the same if we call notifyComplete many times.
        testCase.runTest {
            it.notifyStarting(streamFullRefresh)
            it.notifyComplete(streamFullRefresh)
            it.notifyComplete(streamFullRefresh)
            it.notifyComplete(streamFullRefresh)
        }
        // Check that the outcome is the same if we call notifyFailure afterwards.
        testCase.runTest {
            it.notifyStarting(streamFullRefresh)
            it.notifyComplete(streamFullRefresh)
            it.notifyFailure(streamFullRefresh)
        }
    }

    @Test
    fun testRunningAndIncompleteStream() {
        val testCase =
            TestCase(
                feeds = listOf(streamFullRefresh),
                started = setOf(streamFullRefresh),
                failure = setOf(streamFullRefresh),
            )
        testCase.runTest {
            it.notifyStarting(streamFullRefresh)
            it.notifyFailure(streamFullRefresh)
        }
        // Check that the outcome is the same if we forget to call notifyStarting.
        testCase.runTest { it.notifyFailure(streamFullRefresh) }
        // Check that the outcome is the same if we call notifyFailure many times.
        testCase.runTest {
            it.notifyStarting(streamFullRefresh)
            it.notifyFailure(streamFullRefresh)
            it.notifyFailure(streamFullRefresh)
            it.notifyFailure(streamFullRefresh)
        }
        // Check that the outcome is the same if we call notifyComplete afterwards.
        testCase.runTest {
            it.notifyStarting(streamFullRefresh)
            it.notifyFailure(streamFullRefresh)
            it.notifyComplete(streamFullRefresh)
        }
    }

    @Test
    fun testRunningStreamWithGlobal() {
        val testCase = TestCase(allFeeds, started = setOf(streamIncremental))
        testCase.runTest { it.notifyStarting(streamIncremental) }
        // Check that the outcome is the same if we call notifyStarting with the global feed.
        testCase.runTest { it.notifyStarting(global) }
        testCase.runTest {
            it.notifyStarting(global)
            it.notifyStarting(streamIncremental)
        }
    }

    @Test
    fun testRunningAndCompleteWithGlobal() {
        val testCase =
            TestCase(
                feeds = allFeeds,
                started = setOf(streamIncremental),
                success = setOf(streamIncremental),
            )
        testCase.runTest {
            it.notifyStarting(global)
            it.notifyComplete(global)
            it.notifyStarting(streamIncremental)
            it.notifyComplete(streamIncremental)
        }
        // Check that the outcome is the same if we mix things up a bit.
        testCase.runTest {
            it.notifyStarting(global)
            it.notifyStarting(streamIncremental)
            it.notifyComplete(global)
            it.notifyComplete(streamIncremental)
        }
        testCase.runTest {
            it.notifyStarting(streamIncremental)
            it.notifyStarting(global)
            it.notifyComplete(global)
            it.notifyComplete(streamIncremental)
        }
    }

    @Test
    fun testRunningAndIncompleteAll() {
        val testCase =
            TestCase(
                feeds = allFeeds,
                started = allStreams,
                success = setOf(streamFullRefresh),
                failure = setOf(streamIncremental),
            )
        testCase.runTest {
            it.notifyStarting(streamFullRefresh)
            it.notifyComplete(streamFullRefresh)
            it.notifyStarting(global)
            it.notifyFailure(global)
            it.notifyStarting(streamIncremental)
            it.notifyComplete(streamIncremental)
        }
        // Check that the outcome is the same if we mix things up a bit.
        testCase.runTest {
            it.notifyStarting(streamFullRefresh)
            it.notifyStarting(global)
            it.notifyStarting(streamIncremental)
            it.notifyComplete(streamIncremental)
            it.notifyFailure(global)
            it.notifyComplete(streamFullRefresh)
            it.notifyComplete(global)
        }
    }

    data class TestCase
    private constructor(
        val started: Set<StreamIdentifier>,
        val success: Set<StreamIdentifier>,
        val failure: Set<StreamIdentifier>,
        val feeds: List<Feed>,
    ) {
        constructor(
            feeds: List<Feed>,
            started: Set<Stream> = emptySet(),
            success: Set<Stream> = emptySet(),
            failure: Set<Stream> = emptySet(),
        ) : this(
            started.map { it.id }.toSet(),
            success.map { it.id }.toSet(),
            failure.map { it.id }.toSet(),
            feeds,
        )

        fun runTest(fn: (StreamStatusManager) -> Unit) {
            val started = mutableSetOf<StreamIdentifier>()
            val success = mutableSetOf<StreamIdentifier>()
            val failure = mutableSetOf<StreamIdentifier>()
            val streamStatusManager =
                StreamStatusManager(feeds) {
                    val streamID = StreamIdentifier.from(it.streamDescriptor)
                    when (it.status) {
                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED ->
                            Assertions.assertTrue(started.add(streamID))
                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE ->
                            Assertions.assertTrue(success.add(streamID))
                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE ->
                            Assertions.assertTrue(failure.add(streamID))
                        else -> throw RuntimeException("unexpected status ${it.status}")
                    }
                }
            fn(streamStatusManager)
            Assertions.assertEquals(this.started, started)
            Assertions.assertEquals(this.success, success)
            Assertions.assertEquals(this.failure, failure)
        }
    }
}
