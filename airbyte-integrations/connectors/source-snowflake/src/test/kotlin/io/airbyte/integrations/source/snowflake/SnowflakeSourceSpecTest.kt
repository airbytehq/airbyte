/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Snapshot of the generated connector spec. Regenerate `expected-spec.json` deliberately (run
 * `spec` and format with prettier) whenever the specification class changes; a silent drift here
 * would change what the platform shows to users of saved connections.
 */
class SnowflakeSourceSpecTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected-spec.json")
    }

    @Test
    fun testSpecIsExactlyTheSnapshot() {
        // SyncsTestFixture.testSpec tolerates extra keys in the actual output; this does not.
        val expected: JsonNode =
            Jsons.valueToTree(SyncsTestFixture.specFromResource("expected-spec.json"))
        val actual: JsonNode = Jsons.valueToTree(CliRunner.source("spec").run().specs().last())
        assertEquals(expected, actual)
    }
}
