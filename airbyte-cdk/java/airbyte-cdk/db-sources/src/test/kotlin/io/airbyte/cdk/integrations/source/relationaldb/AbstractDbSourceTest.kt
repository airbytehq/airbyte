/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.source.jdbc.AbstractDbSourceForTest
import io.airbyte.cdk.integrations.source.relationaldb.state.*
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import java.io.IOException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.mockito.Mockito
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables
import uk.org.webcompere.systemstubs.jupiter.SystemStub
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension

/** Test suite for the [AbstractDbSource] class. */
@ExtendWith(SystemStubsExtension::class)
class AbstractDbSourceTest {
    @SystemStub private val environmentVariables: EnvironmentVariables? = null

    @Test
    @Throws(IOException::class)
    fun testDeserializationOfLegacyState() {
        val dbSource =
            Mockito.mock(
                AbstractDbSourceForTest::class.java,
                Mockito.withSettings().useConstructor("").defaultAnswer(Mockito.CALLS_REAL_METHODS)
            )
        val config = Mockito.mock(JsonNode::class.java)

        val legacyStateJson = MoreResources.readResource("states/legacy.json")
        val legacyState = Jsons.deserialize(legacyStateJson)

        val result =
            StateGeneratorUtils.deserializeInitialState(
                legacyState,
                dbSource.getSupportedStateType(config)
            )
        Assertions.assertEquals(1, result.size)
        Assertions.assertEquals(AirbyteStateMessage.AirbyteStateType.LEGACY, result[0].type)
    }

    @Test
    @Throws(IOException::class)
    fun testDeserializationOfGlobalState() {
        val dbSource =
            Mockito.mock(
                AbstractDbSourceForTest::class.java,
                Mockito.withSettings().useConstructor("").defaultAnswer(Mockito.CALLS_REAL_METHODS)
            )
        val config = Mockito.mock(JsonNode::class.java)

        val globalStateJson = MoreResources.readResource("states/global.json")
        val globalState = Jsons.deserialize(globalStateJson)

        val result =
            StateGeneratorUtils.deserializeInitialState(
                globalState,
                dbSource.getSupportedStateType(config)
            )
        Assertions.assertEquals(1, result.size)
        Assertions.assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, result[0].type)
    }

    @Test
    @Throws(IOException::class)
    fun testDeserializationOfStreamState() {
        val dbSource =
            Mockito.mock(
                AbstractDbSourceForTest::class.java,
                Mockito.withSettings().useConstructor("").defaultAnswer(Mockito.CALLS_REAL_METHODS)
            )
        val config = Mockito.mock(JsonNode::class.java)

        val streamStateJson = MoreResources.readResource("states/per_stream.json")
        val streamState = Jsons.deserialize(streamStateJson)

        val result =
            StateGeneratorUtils.deserializeInitialState(
                streamState,
                dbSource.getSupportedStateType(config)
            )
        Assertions.assertEquals(2, result.size)
        Assertions.assertEquals(AirbyteStateMessage.AirbyteStateType.STREAM, result[0].type)
    }

    @Test
    @Throws(IOException::class)
    fun testDeserializationOfNullState() {
        val dbSource =
            Mockito.mock(
                AbstractDbSourceForTest::class.java,
                Mockito.withSettings().useConstructor("").defaultAnswer(Mockito.CALLS_REAL_METHODS)
            )
        val config = Mockito.mock(JsonNode::class.java)

        val result =
            StateGeneratorUtils.deserializeInitialState(
                null,
                dbSource.getSupportedStateType(config)
            )
        Assertions.assertEquals(1, result.size)
        Assertions.assertEquals(dbSource.getSupportedStateType(config), result[0].type)
    }
}
