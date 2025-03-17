/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.netsuite

import io.airbyte.cdk.command.SyncsTestFixture
import org.junit.jupiter.api.Test

class NetsuiteSourceSpecTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected-spec.json")
    }
}
