/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.spec

import com.deblock.jsondiff.DiffGenerator
import com.deblock.jsondiff.diff.JsonDiff
import com.deblock.jsondiff.matcher.CompositeJsonMatcher
import com.deblock.jsondiff.matcher.JsonMatcher
import com.deblock.jsondiff.matcher.LenientJsonObjectPartialMatcher
import com.deblock.jsondiff.matcher.StrictJsonArrayPartialMatcher
import com.deblock.jsondiff.matcher.StrictPrimitivePartialMatcher
import com.deblock.jsondiff.viewer.OnlyErrorDiffViewer
import io.airbyte.cdk.test.util.DestinationProcessFactory
import io.airbyte.cdk.test.util.FakeDataDumper
import io.airbyte.cdk.test.util.IntegrationTest
import io.airbyte.cdk.test.util.NoopDestinationCleaner
import io.airbyte.cdk.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

private const val EXPECTED_SPEC_FILENAME = "expected-spec.json"
private val expectedSpecPath = Path.of(EXPECTED_SPEC_FILENAME)

/**
 * This is largely copied from [io.airbyte.cdk.spec.SpecTest], but adapted to use our
 * [DestinationProcessFactory].
 *
 * It also automatically writes the actual spec back to `expected-spec.json` for easier inspection
 * of the diff. This diff is _really messy_ for the initial migration from the old CDK to the new
 * one, but after that, it should be pretty readable.
 */
abstract class SpecTest :
    IntegrationTest(
        FakeDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
    ) {
    @Test
    fun testSpec() {
        if (!Files.exists(expectedSpecPath)) {
            Files.createFile(expectedSpecPath)
        }
        val expectedSpec = Files.readString(expectedSpecPath)
        val process = destinationProcessFactory.createDestinationProcess("spec")
        process.run()
        val messages = process.readMessages()
        val specMessages = messages.filter { it.type == AirbyteMessage.Type.SPEC }

        assertEquals(
            specMessages.size,
            1,
            "Expected to receive exactly one connection status message, but got ${specMessages.size}: $specMessages"
        )

        val spec = specMessages.first().spec
        val actualSpecPrettyPrint: String =
            Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(spec)
        Files.write(expectedSpecPath, actualSpecPrettyPrint.toByteArray())

        val jsonMatcher: JsonMatcher =
            CompositeJsonMatcher(
                StrictJsonArrayPartialMatcher(),
                LenientJsonObjectPartialMatcher(),
                StrictPrimitivePartialMatcher(),
            )
        val diff: JsonDiff =
            DiffGenerator.diff(expectedSpec, Jsons.writeValueAsString(spec), jsonMatcher)
        assertAll(
            "Spec snapshot test failed. Run this test locally and then `git diff <...>/expected_spec.json` to see what changed, and commit the diff if that change was intentional.",
            { assertEquals("", OnlyErrorDiffViewer.from(diff).toString()) },
            { assertEquals(expectedSpec, actualSpecPrettyPrint) }
        )
    }
}
