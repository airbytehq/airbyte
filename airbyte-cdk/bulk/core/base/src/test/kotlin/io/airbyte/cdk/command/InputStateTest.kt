/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
class InputStateTest {
    @Inject lateinit var actual: InputState

    @Test
    fun testEmpty() {
        Assertions.assertEquals(EmptyInputState, actual)
    }

    @Test
    @Property(
        name = "airbyte.connector.state.resource",
        value = "command/vanilla-stream-states.json",
    )
    fun testVanillaStreamStates() {
        val expected =
            StreamInputState(
                mapOf(
                    AirbyteStreamNameNamespacePair("bar", "foo") to
                        Jsons.readTree("{\"primary_key\":{\"k1\":10,\"k2\":20}}"),
                    AirbyteStreamNameNamespacePair("baz", "foo") to
                        Jsons.readTree("{\"cursors\":{\"c\":30}}"),
                ),
            )
        Assertions.assertEquals(
            Jsons.writeValueAsString(expected),
            Jsons.writeValueAsString(actual),
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.state.resource",
        value = "command/vanilla-global-states.json",
    )
    fun testVanillaGlobalStates() {
        val expected =
            GlobalInputState(
                global = Jsons.readTree("{\"cdc\":{}}"),
                globalStreams =
                    mapOf(
                        AirbyteStreamNameNamespacePair("bar", "foo") to
                            Jsons.readTree("{\"primary_key\":{\"k1\":10,\"k2\":20}}"),
                    ),
                nonGlobalStreams = mapOf(),
            )
        Assertions.assertEquals(
            Jsons.writeValueAsString(expected),
            Jsons.writeValueAsString(actual),
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.state.resource",
        value = "command/vanilla-mixed-states.json",
    )
    fun testVanillaMixedStates() {
        val expected =
            GlobalInputState(
                global = Jsons.readTree("{\"cdc\":{}}"),
                globalStreams =
                    mapOf(
                        AirbyteStreamNameNamespacePair("bar", "foo") to
                            Jsons.readTree("{\"primary_key\":{\"k1\":10,\"k2\":20}}"),
                    ),
                nonGlobalStreams =
                    mapOf(
                        AirbyteStreamNameNamespacePair("baz", "foo") to
                            Jsons.readTree("{\"primary_key\":{\"k\":1}}"),
                    ),
            )
        Assertions.assertEquals(
            Jsons.writeValueAsString(expected),
            Jsons.writeValueAsString(actual),
        )
    }

    @Test
    @Property(name = "airbyte.connector.state.resource", value = "command/duplicate-states.json")
    fun testDuplicates() {
        val expected =
            GlobalInputState(
                global = Jsons.readTree("{\"cdc\":{}}"),
                globalStreams =
                    mapOf(
                        AirbyteStreamNameNamespacePair("bar", "foo") to
                            Jsons.readTree("{\"primary_key\":{\"k1\":10,\"k2\":20}}"),
                    ),
                nonGlobalStreams =
                    mapOf(
                        AirbyteStreamNameNamespacePair("baz", "foo") to
                            Jsons.readTree("{\"primary_key\":{\"k\":10}}"),
                    ),
            )
        Assertions.assertEquals(
            Jsons.writeValueAsString(expected),
            Jsons.writeValueAsString(actual),
        )
    }
}
