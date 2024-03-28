/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.integrations.base.DestinationConfig.Companion.clearInstance
import io.airbyte.cdk.integrations.base.DestinationConfig.Companion.initialize
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.concurrent.atomic.AtomicLong
import java.util.function.Supplier
import java.util.stream.IntStream
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class TypeAndDedupeOperationValveTest {
    private var minuteUpdates: Supplier<Long>? = null

    @BeforeEach
    fun setup() {
        val start = AtomicLong(0)
        minuteUpdates = Supplier { start.getAndUpdate { l: Long -> l + (60 * 1000) } }
    }

    @AfterEach
    fun clearDestinationConfig() {
        clearInstance()
    }

    private fun initializeDestinationConfigOption(enableIncrementalTypingAndDeduping: Boolean) {
        val mapper = ObjectMapper()
        val objectNode = mapper.createObjectNode()
        objectNode.put("enable_incremental_final_table_updates", enableIncrementalTypingAndDeduping)
        initialize(objectNode)
    }

    private fun elapseTime(timing: Supplier<Long>?, iterations: Int) {
        IntStream.range(0, iterations).forEach { `__`: Int -> timing!!.get() }
    }

    @ParameterizedTest
    @ValueSource(booleans = [true, false])
    fun testAddStream(enableIncrementalTypingAndDeduping: Boolean) {
        initializeDestinationConfigOption(enableIncrementalTypingAndDeduping)
        val valve = TypeAndDedupeOperationValve(ALWAYS_ZERO)
        valve.addStream(STREAM_A)
        Assertions.assertEquals(-1, valve.getIncrementInterval(STREAM_A))
        Assertions.assertEquals(
            valve.readyToTypeAndDedupe(STREAM_A),
            enableIncrementalTypingAndDeduping
        )
        Assertions.assertEquals(valve[STREAM_A], 0L)
    }

    @ParameterizedTest
    @ValueSource(booleans = [true, false])
    fun testReadyToTypeAndDedupe(enableIncrementalTypingAndDeduping: Boolean) {
        initializeDestinationConfigOption(enableIncrementalTypingAndDeduping)
        val valve = TypeAndDedupeOperationValve(minuteUpdates!!)
        // method call increments time
        valve.addStream(STREAM_A)
        elapseTime(minuteUpdates, 1)
        // method call increments time
        valve.addStream(STREAM_B)
        // method call increments time
        Assertions.assertEquals(
            valve.readyToTypeAndDedupe(STREAM_A),
            enableIncrementalTypingAndDeduping
        )
        elapseTime(minuteUpdates, 1)
        Assertions.assertEquals(
            valve.readyToTypeAndDedupe(STREAM_B),
            enableIncrementalTypingAndDeduping
        )
        valve.updateTimeAndIncreaseInterval(STREAM_A)
        Assertions.assertEquals((1000 * 60 * 60 * 6).toLong(), valve.getIncrementInterval(STREAM_A))
        // method call increments time
        Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A))
        // More than enough time has passed now
        elapseTime(minuteUpdates, 60 * 6)
        Assertions.assertEquals(
            valve.readyToTypeAndDedupe(STREAM_A),
            enableIncrementalTypingAndDeduping
        )
    }

    @ParameterizedTest
    @ValueSource(booleans = [true, false])
    fun testUpdateTimeAndIncreaseInterval(enableIncrementalTypingAndDeduping: Boolean) {
        initializeDestinationConfigOption(enableIncrementalTypingAndDeduping)
        val valve = TypeAndDedupeOperationValve(minuteUpdates!!)
        valve.addStream(STREAM_A)
        IntStream.range(0, 1).forEach { `__`: Int ->
            Assertions.assertEquals(
                valve.readyToTypeAndDedupe(STREAM_A),
                enableIncrementalTypingAndDeduping
            )
        } // start
        // ready
        // to T&D
        Assertions.assertEquals(
            valve.readyToTypeAndDedupe(STREAM_A),
            enableIncrementalTypingAndDeduping
        )
        valve.updateTimeAndIncreaseInterval(STREAM_A)
        IntStream.range(0, 360).forEach { `__`: Int ->
            Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A))
        }
        Assertions.assertEquals(
            valve.readyToTypeAndDedupe(STREAM_A),
            enableIncrementalTypingAndDeduping
        )
    }

    companion object {
        private val STREAM_A = AirbyteStreamNameNamespacePair("a", "a")
        private val STREAM_B = AirbyteStreamNameNamespacePair("b", "b")
        private val ALWAYS_ZERO = Supplier { 0L }
    }
}
