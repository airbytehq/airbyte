/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import com.deblock.jsondiff.DiffGenerator
import com.deblock.jsondiff.diff.JsonDiff
import com.deblock.jsondiff.matcher.CompositeJsonMatcher
import com.deblock.jsondiff.matcher.JsonMatcher
import com.deblock.jsondiff.matcher.LenientJsonObjectPartialMatcher
import com.deblock.jsondiff.matcher.StrictJsonArrayPartialMatcher
import com.deblock.jsondiff.matcher.StrictPrimitivePartialMatcher
import com.deblock.jsondiff.viewer.OnlyErrorDiffViewer
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.cdk.operation.CONNECTOR_OPERATION
import io.airbyte.cdk.operation.SpecOperation
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.Property
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test


@MicronautTest(environments = ["source"])
@Property(name = CONNECTOR_OPERATION, value = "spec")
class OracleSourceSpecTest {

    @Inject lateinit var specOperation: SpecOperation

    private var latestSpec = ConnectorSpecification()

    @MockBean(OutputConsumer::class)
    fun outputConsumer() = OutputConsumer {
        latestSpec = it.spec
    }

    @Test
    internal fun testSpec() {
        val expected: String = MoreResources.readResource("expected-spec.json")
        specOperation.execute()
        val actual: String = Jsons.serialize(latestSpec)

        val jsonMatcher: JsonMatcher = CompositeJsonMatcher(
            StrictJsonArrayPartialMatcher(),
            LenientJsonObjectPartialMatcher(),
            StrictPrimitivePartialMatcher(),
        )
        val diff: JsonDiff = DiffGenerator.diff(expected, actual, jsonMatcher)
        Assertions.assertEquals("", OnlyErrorDiffViewer.from(diff).toString())
    }
}
