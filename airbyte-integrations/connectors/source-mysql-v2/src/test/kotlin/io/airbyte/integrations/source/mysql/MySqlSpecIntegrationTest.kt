package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.SyncsTestFixture
import org.junit.jupiter.api.Test

class MySqlSpecIntegrationTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected-spec.json")
    }
}
