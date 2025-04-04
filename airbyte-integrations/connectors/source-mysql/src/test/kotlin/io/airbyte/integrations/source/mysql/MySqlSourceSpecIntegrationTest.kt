/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.SyncsTestFixture
import org.junit.jupiter.api.Test

class MySqlSourceSpecIntegrationTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected-spec.json")
    }
}
