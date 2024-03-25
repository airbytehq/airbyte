/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import java.util.function.Consumer

internal class SwitchingDestinationTest {
    internal enum class SwitchingEnum {
        INSERT,
        COPY
    }

    private var insertDestination: Destination? = null
    private var copyDestination: Destination? = null
    private var destinationMap: Map<SwitchingEnum, Destination?>? = null

    @BeforeEach
    fun setUp() {
        insertDestination = Mockito.mock(Destination::class.java)
        copyDestination = Mockito.mock(Destination::class.java)
        destinationMap = ImmutableMap.of(
                SwitchingEnum.INSERT, insertDestination,
                SwitchingEnum.COPY, copyDestination)
    }

    @Test
    @Throws(Exception::class)
    fun testInsert() {
        val switchingDestination = SwitchingDestination(SwitchingEnum::class.java, { c: JsonNode? -> SwitchingEnum.INSERT }, destinationMap)

        switchingDestination.getConsumer(Mockito.mock(JsonNode::class.java), Mockito.mock(ConfiguredAirbyteCatalog::class.java), Mockito.mock(Consumer::class.java))

        Mockito.verify(insertDestination, Mockito.times(1)).getConsumer(ArgumentMatchers.any(), ArgumentMatchers.any(), ArgumentMatchers.any())
        Mockito.verify(copyDestination, Mockito.times(0)).getConsumer(ArgumentMatchers.any(), ArgumentMatchers.any(), ArgumentMatchers.any())

        switchingDestination.check(Mockito.mock(JsonNode::class.java))

        Mockito.verify(insertDestination, Mockito.times(1)).check(ArgumentMatchers.any())
        Mockito.verify(copyDestination, Mockito.times(0)).check(ArgumentMatchers.any())
    }

    @Test
    @Throws(Exception::class)
    fun testCopy() {
        val switchingDestination = SwitchingDestination(SwitchingEnum::class.java, { c: JsonNode? -> SwitchingEnum.COPY }, destinationMap)

        switchingDestination.getConsumer(Mockito.mock(JsonNode::class.java), Mockito.mock(ConfiguredAirbyteCatalog::class.java), Mockito.mock(Consumer::class.java))

        Mockito.verify(insertDestination, Mockito.times(0)).getConsumer(ArgumentMatchers.any(), ArgumentMatchers.any(), ArgumentMatchers.any())
        Mockito.verify(copyDestination, Mockito.times(1)).getConsumer(ArgumentMatchers.any(), ArgumentMatchers.any(), ArgumentMatchers.any())

        switchingDestination.check(Mockito.mock(JsonNode::class.java))

        Mockito.verify(insertDestination, Mockito.times(0)).check(ArgumentMatchers.any())
        Mockito.verify(copyDestination, Mockito.times(1)).check(ArgumentMatchers.any())
    }
}
