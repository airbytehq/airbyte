/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import org.junit.jupiter.api.Test

class SyncsTestFixtureTest {

    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("fakesource/expected-spec.json")
    }
}
