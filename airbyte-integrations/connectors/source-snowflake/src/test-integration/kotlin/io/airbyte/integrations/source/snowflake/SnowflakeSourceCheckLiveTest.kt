/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.command.SyncsTestFixture
import org.junit.jupiter.api.Test

class SnowflakeSourceCheckLiveTest : AbstractSnowflakeLiveTest() {

    @Test
    fun checkSucceeds() {
        SyncsTestFixture.testCheck(spec())
    }

    @Test
    fun checkFailsOnMissingSchema() {
        SyncsTestFixture.testCheck(
            SnowflakeLiveTestSupport.spec(schema = "NOSUCHSCHEMA$schema"),
            expectedFailure = "schema does not exist or not authorized",
        )
    }

    @Test
    fun checkFailsOnMissingWarehouse() {
        // Without validateDefaultParameters the session opens and CHECK passes: SHOW commands and
        // LIMIT 0 probes do not need a warehouse.
        val spec = spec().apply { warehouse = "NOSUCHWAREHOUSE$schema" }
        SyncsTestFixture.testCheck(
            spec,
            expectedFailure = "warehouse does not exist or not authorized"
        )
    }

    @Test
    fun checkFailsOnMissingDatabase() {
        val spec = spec().apply { database = "NOSUCHDATABASE$schema" }
        SyncsTestFixture.testCheck(
            spec,
            expectedFailure = "database does not exist or not authorized"
        )
    }
}
