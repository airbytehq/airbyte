/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.spec

import com.deblock.jsondiff.DiffGenerator
import com.deblock.jsondiff.matcher.CompositeJsonMatcher
import com.deblock.jsondiff.matcher.JsonMatcher
import com.deblock.jsondiff.matcher.StrictJsonArrayPartialMatcher
import com.deblock.jsondiff.matcher.StrictJsonObjectPartialMatcher
import com.deblock.jsondiff.matcher.StrictPrimitivePartialMatcher
import com.deblock.jsondiff.viewer.OnlyErrorDiffViewer
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.command.EnvVarConstants.AIRBYTE_EDITION
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.deserializeToPrettyPrintedString
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.nio.file.Files
import java.nio.file.Path
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

/**
 * This is largely copied from [io.airbyte.cdk.spec.SpecTest], but adapted to use our
 * [DestinationProcessFactory].
 *
 * It also automatically writes the actual spec back to `expected-spec.json` for easier inspection
 * of the diff. This diff is _really messy_ for the initial migration from the old CDK to the new
 * one, but after that, it should be pretty readable.
 */
abstract class SpecTest(
    additionalMicronautEnvs: List<String> = emptyList(),
    micronautProperties: Map<Property, String> = emptyMap(),
) :
    IntegrationTest(
        additionalMicronautEnvs = additionalMicronautEnvs,
        dataDumper = FakeDataDumper,
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = NoopExpectedRecordMapper,
        micronautProperties = micronautProperties,
    ) {
    private val testResourcesPath = Path.of("src/test-integration/resources")

    @Test
    fun testSpecOss() {
        testSpec(
            expectedSpecFilename = "expected-spec-oss.json",
            additionalProperties = mapOf(AIRBYTE_EDITION to "OSS")
        )
    }

    @Test
    fun testSpecCloud() {
        testSpec(
            expectedSpecFilename = "expected-spec-cloud.json",
            additionalProperties = mapOf(AIRBYTE_EDITION to "CLOUD"),
            featureFlags = arrayOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)
        )
    }

    private fun testSpec(
        expectedSpecFilename: String,
        additionalProperties: Map<Property, String> = emptyMap(),
        vararg featureFlags: FeatureFlag,
    ) {
        val expectedSpecPath = testResourcesPath.resolve(expectedSpecFilename)

        if (!Files.exists(expectedSpecPath)) {
            Files.createDirectories(testResourcesPath)
            Files.createFile(expectedSpecPath)
        }
        val expectedSpec = Files.readString(expectedSpecPath)
        val process =
            destinationProcessFactory.createDestinationProcess(
                "spec",
                featureFlags = featureFlags,
                micronautProperties = micronautProperties + additionalProperties,
            )
        runBlocking { process.run() }
        val messages = process.readMessages()
        val specMessages = messages.filter { it.type == AirbyteMessage.Type.SPEC }

        Assertions.assertEquals(
            specMessages.size,
            1,
            "Expected to receive exactly one connection status message, but got ${specMessages.size}: $specMessages"
        )

        val spec = specMessages.first().spec
        val actualSpecPrettyPrint: String = spec.deserializeToPrettyPrintedString()
        Files.write(expectedSpecPath, actualSpecPrettyPrint.toByteArray())

        val jsonMatcher: JsonMatcher =
            CompositeJsonMatcher(
                StrictJsonArrayPartialMatcher(),
                StrictJsonObjectPartialMatcher(),
                StrictPrimitivePartialMatcher(),
            )
        val diff =
            OnlyErrorDiffViewer.from(
                    DiffGenerator.diff(expectedSpec, Jsons.writeValueAsString(spec), jsonMatcher)
                )
                .toString()
        assertAll(
            "Spec snapshot test failed. Run this test locally and then `git diff <...>/$expectedSpecFilename` to see what changed, and commit the diff if that change was intentional.",
            {
                Assertions.assertTrue(
                    diff.isEmpty(),
                    "Detected semantic diff in JSON:\n" + diff.prependIndent("\t\t")
                )
            },
            {
                Assertions.assertTrue(
                    expectedSpec == actualSpecPrettyPrint,
                    "File contents did not equal generated spec, see git diff for details"
                )
            }
        )
    }
}
