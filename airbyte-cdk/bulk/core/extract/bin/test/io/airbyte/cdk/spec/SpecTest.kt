/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.spec

import com.deblock.jsondiff.DiffGenerator
import com.deblock.jsondiff.diff.JsonDiff
import com.deblock.jsondiff.matcher.CompositeJsonMatcher
import com.deblock.jsondiff.matcher.JsonMatcher
import com.deblock.jsondiff.matcher.LenientJsonObjectPartialMatcher
import com.deblock.jsondiff.matcher.StrictJsonArrayPartialMatcher
import com.deblock.jsondiff.matcher.StrictPrimitivePartialMatcher
import com.deblock.jsondiff.viewer.OnlyErrorDiffViewer
import io.airbyte.cdk.Operation
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["source"], rebuildContext = true)
@Property(name = Operation.PROPERTY, value = "spec")
@Property(name = "airbyte.connector.metadata.documentation-url", value = "https://docs.airbyte.com")
class SpecTest {
    @Inject lateinit var specOperation: SpecOperation

    @Inject lateinit var outputConsumer: BufferingOutputConsumer

    @Test
    fun testSpec() {
        val expected: String = ResourceUtils.readResource("fakesource/expected-spec.json")
        specOperation.execute()
        val actual: String = Jsons.writeValueAsString(outputConsumer.specs().last())

        val jsonMatcher: JsonMatcher =
            CompositeJsonMatcher(
                StrictJsonArrayPartialMatcher(),
                LenientJsonObjectPartialMatcher(),
                StrictPrimitivePartialMatcher(),
            )
        val diff: JsonDiff = DiffGenerator.diff(expected, actual, jsonMatcher)
        Assertions.assertEquals("", OnlyErrorDiffViewer.from(diff).toString())
    }
}
