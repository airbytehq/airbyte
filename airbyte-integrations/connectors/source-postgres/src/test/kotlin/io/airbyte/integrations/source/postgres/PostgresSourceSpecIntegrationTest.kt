package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.SyncsTestFixture
import org.junit.jupiter.api.Test

class PostgresSourceSpecIntegrationTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected-spec.json")
    }
}
