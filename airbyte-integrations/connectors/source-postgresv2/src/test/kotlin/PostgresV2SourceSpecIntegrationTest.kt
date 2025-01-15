
package io.airbyte.integrations.source.postgresv2
import io.airbyte.cdk.command.SyncsTestFixture
import org.junit.jupiter.api.Test

class PostgresV2SourceSpecIntegrationTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected-spec.json")
    }
}
