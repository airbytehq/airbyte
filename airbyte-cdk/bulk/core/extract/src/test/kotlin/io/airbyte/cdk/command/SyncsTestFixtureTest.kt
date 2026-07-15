/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import org.junit.jupiter.api.Test

class SyncsTestFixtureTest {

    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("fakesource/expected-spec.json")
    }
}
