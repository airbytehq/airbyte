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
import org.mockito.Mockito
import org.mockito.Mockito.mock
import org.mockito.kotlin.any

internal class SwitchingDestinationTest {
    internal enum class SwitchingEnum {
        INSERT,
        COPY
    }

    private lateinit var insertDestination: Destination
    private lateinit var copyDestination: Destination
    private lateinit var destinationMap: Map<SwitchingEnum, Destination>

    @BeforeEach
    fun setUp() {
        insertDestination = Mockito.mock(Destination::class.java)
        copyDestination = Mockito.mock(Destination::class.java)
        destinationMap =
            ImmutableMap.of(
                SwitchingEnum.INSERT,
                insertDestination,
                SwitchingEnum.COPY,
                copyDestination
            )
    }

    @Test
    @Throws(Exception::class)
    fun testInsert() {
        val switchingDestination =
            SwitchingDestination(
                SwitchingEnum::class.java,
                { c: JsonNode -> SwitchingEnum.INSERT },
                destinationMap
            )

        switchingDestination.getConsumer(
            Mockito.mock(JsonNode::class.java),
            Mockito.mock(ConfiguredAirbyteCatalog::class.java),
            mock()
        )

        Mockito.verify(insertDestination, Mockito.times(1)).getConsumer(any(), any(), any())
        Mockito.verify(copyDestination, Mockito.times(0)).getConsumer(any(), any(), any())

        switchingDestination.check(Mockito.mock(JsonNode::class.java))

        Mockito.verify(insertDestination, Mockito.times(1)).check(any())
        Mockito.verify(copyDestination, Mockito.times(0)).check(any())
    }

    @Test
    @Throws(Exception::class)
    fun testCopy() {
        val switchingDestination =
            SwitchingDestination(
                SwitchingEnum::class.java,
                { c: JsonNode -> SwitchingEnum.COPY },
                destinationMap
            )

        switchingDestination.getConsumer(
            Mockito.mock(JsonNode::class.java),
            Mockito.mock(ConfiguredAirbyteCatalog::class.java),
            Mockito.mock()
        )

        Mockito.verify(insertDestination, Mockito.times(0)).getConsumer(any(), any(), any())
        Mockito.verify(copyDestination, Mockito.times(1)).getConsumer(any(), any(), any())

        switchingDestination.check(Mockito.mock(JsonNode::class.java))

        Mockito.verify(insertDestination, Mockito.times(0)).check(any())
        Mockito.verify(copyDestination, Mockito.times(1)).check(any())
    }
}
