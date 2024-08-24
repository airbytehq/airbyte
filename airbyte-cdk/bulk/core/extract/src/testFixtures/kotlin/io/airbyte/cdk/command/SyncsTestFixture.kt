/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.deblock.jsondiff.DiffGenerator
import com.deblock.jsondiff.diff.JsonDiff
import com.deblock.jsondiff.matcher.CompositeJsonMatcher
import com.deblock.jsondiff.matcher.JsonMatcher
import com.deblock.jsondiff.matcher.StrictJsonArrayPartialMatcher
import com.deblock.jsondiff.matcher.StrictJsonObjectPartialMatcher
import com.deblock.jsondiff.matcher.StrictPrimitivePartialMatcher
import com.deblock.jsondiff.viewer.OnlyErrorDiffViewer
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.sql.Connection
import java.util.function.Supplier
import org.junit.jupiter.api.Assertions

data object SyncsTestFixture {
    fun testSpec(expectedSpec: ConnectorSpecification) {
        val expected: String = Jsons.writeValueAsString(expectedSpec)
        val output: BufferingOutputConsumer = CliRunner.runSource("spec")
        val actual: String = Jsons.writeValueAsString(output.specs().last())

        val jsonMatcher: JsonMatcher =
            CompositeJsonMatcher(
                StrictJsonArrayPartialMatcher(),
                StrictJsonObjectPartialMatcher(),
                StrictPrimitivePartialMatcher(),
            )
        val diff: JsonDiff = DiffGenerator.diff(expected, actual, jsonMatcher)
        Assertions.assertEquals("", OnlyErrorDiffViewer.from(diff).toString())
    }

    fun testSpec(expectedSpecResource: String) {
        testSpec(specFromResource(expectedSpecResource))
    }

    fun specFromResource(specResource: String): ConnectorSpecification =
        Jsons.readValue(
            ResourceUtils.readResource(specResource),
            ConnectorSpecification::class.java,
        )

    fun testCheck(
        configPojo: ConfigurationJsonObjectBase,
        expectedFailure: String? = null,
    ) {
        val checkOutput: BufferingOutputConsumer = CliRunner.runSource("check", configPojo)
        Assertions.assertEquals(1, checkOutput.statuses().size, checkOutput.statuses().toString())
        if (expectedFailure == null) {
            Assertions.assertEquals(
                AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED),
                checkOutput.statuses().first(),
            )
        } else {
            Assertions.assertEquals(
                AirbyteConnectionStatus.Status.FAILED,
                checkOutput.statuses().first().status,
            )
            val msg: String? = checkOutput.statuses().first().message
            Assertions.assertTrue(msg != null && msg.contains(expectedFailure.toRegex()), msg)
        }
    }

    fun testDiscover(
        configPojo: ConfigurationJsonObjectBase,
        expectedCatalog: AirbyteCatalog,
    ) {
        val discoverOutput: BufferingOutputConsumer = CliRunner.runSource("discover", configPojo)
        Assertions.assertEquals(listOf(expectedCatalog), discoverOutput.catalogs())
    }

    fun testDiscover(
        configPojo: ConfigurationJsonObjectBase,
        expectedCatalogResource: String,
    ) {
        testDiscover(configPojo, catalogFromResource(expectedCatalogResource))
    }

    fun catalogFromResource(catalogResource: String): AirbyteCatalog =
        Jsons.readValue(
            ResourceUtils.readResource(catalogResource),
            AirbyteCatalog::class.java,
        )

    fun <T : ConfigurationJsonObjectBase> testReads(
        configPojo: T,
        connectionSupplier: Supplier<Connection>,
        prelude: (Connection) -> Unit,
        configuredCatalog: ConfiguredAirbyteCatalog,
        initialState: List<AirbyteStateMessage> = listOf(),
        vararg afterRead: AfterRead,
    ) {
        connectionSupplier.get().use(prelude)
        var state: List<AirbyteStateMessage> = initialState
        for (step in afterRead) {
            val readOutput: BufferingOutputConsumer =
                CliRunner.runSource("read", configPojo, configuredCatalog, state)
            step.validate(readOutput)
            connectionSupplier.get().use(step::update)
            state = readOutput.states()
        }
    }

    fun <T : ConfigurationJsonObjectBase> testReads(
        configPojo: T,
        connectionSupplier: Supplier<Connection>,
        prelude: (Connection) -> Unit,
        configuredCatalogResource: String,
        initialStateResource: String?,
        vararg afterRead: AfterRead,
    ) {
        testReads(
            configPojo,
            connectionSupplier,
            prelude,
            configuredCatalogFromResource(configuredCatalogResource),
            initialStateFromResource(initialStateResource),
            *afterRead,
        )
    }

    fun <T : ConfigurationJsonObjectBase> testSyncs(
        configPojo: T,
        connectionSupplier: Supplier<Connection>,
        prelude: (Connection) -> Unit,
        expectedCatalog: AirbyteCatalog,
        configuredCatalog: ConfiguredAirbyteCatalog,
        vararg afterRead: AfterRead,
    ) {
        connectionSupplier.get().use(prelude)
        testCheck(configPojo)
        testDiscover(configPojo, expectedCatalog)
        var state: List<AirbyteStateMessage> = listOf()
        for (step in afterRead) {
            val readOutput: BufferingOutputConsumer =
                CliRunner.runSource("read", configPojo, configuredCatalog, state)
            step.validate(readOutput)
            connectionSupplier.get().use(step::update)
            state = readOutput.states()
        }
    }

    fun <T : ConfigurationJsonObjectBase> testSyncs(
        configPojo: T,
        connectionSupplier: Supplier<Connection>,
        prelude: (Connection) -> Unit,
        expectedCatalogResource: String,
        configuredCatalogResource: String,
        vararg afterRead: AfterRead,
    ) {
        testSyncs(
            configPojo,
            connectionSupplier,
            prelude,
            catalogFromResource(expectedCatalogResource),
            configuredCatalogFromResource(configuredCatalogResource),
            *afterRead,
        )
    }

    fun configuredCatalogFromResource(configuredCatalogResource: String): ConfiguredAirbyteCatalog =
        Jsons.readValue(
            ResourceUtils.readResource(configuredCatalogResource),
            ConfiguredAirbyteCatalog::class.java,
        )

    fun initialStateFromResource(initialStateResource: String?): List<AirbyteStateMessage> =
        if (initialStateResource == null) {
            listOf()
        } else {
            val initialStateJson: String = ResourceUtils.readResource(initialStateResource)
            ValidatedJsonUtils.parseList(AirbyteStateMessage::class.java, initialStateJson)
        }

    interface AfterRead {
        fun validate(actualOutput: BufferingOutputConsumer)

        fun update(connection: Connection)

        companion object {
            fun fromExpectedMessages(
                expectedMessages: List<AirbyteMessage>,
                update: (Connection) -> Unit = {},
            ): AfterRead =
                object : AfterRead {
                    override fun validate(actualOutput: BufferingOutputConsumer) {
                        // State messages are timing-sensitive and therefore non-deterministic.
                        // Ignore them for now.
                        val expectedWithoutStates: List<AirbyteMessage> =
                            expectedMessages
                                .filterNot { it.type == AirbyteMessage.Type.STATE }
                                .sortedBy { Jsons.writeValueAsString(it) }
                        val actualWithoutStates: List<AirbyteMessage> =
                            actualOutput
                                .messages()
                                .filterNot { it.type == AirbyteMessage.Type.STATE }
                                .sortedBy { Jsons.writeValueAsString(it) }
                        Assertions.assertIterableEquals(expectedWithoutStates, actualWithoutStates)
                        // Check for state message counts (null if no state messages).
                        val expectedCount: Double? =
                            expectedMessages
                                .filter { it.type == AirbyteMessage.Type.STATE }
                                .mapNotNull { it.state?.sourceStats?.recordCount }
                                .reduceRightOrNull { a: Double, b: Double -> a + b }
                        val actualCount: Double? =
                            actualOutput
                                .messages()
                                .filter { it.type == AirbyteMessage.Type.STATE }
                                .mapNotNull { it.state?.sourceStats?.recordCount }
                                .reduceRightOrNull { a: Double, b: Double -> a + b }
                        Assertions.assertEquals(expectedCount, actualCount)
                    }

                    override fun update(connection: Connection) {
                        update(connection)
                    }
                }

            fun fromExpectedMessages(
                expectedMessagesResource: String,
                update: (Connection) -> Unit = {},
            ): AfterRead =
                fromExpectedMessages(messagesFromResource(expectedMessagesResource), update)
        }
    }

    fun messagesFromResource(messagesResource: String): List<AirbyteMessage> =
        Jsons.readTree(ResourceUtils.readResource(messagesResource))
            .elements()
            .asSequence()
            .mapNotNull { Jsons.treeToValue(it, AirbyteMessage::class.java) }
            .toList()
}
