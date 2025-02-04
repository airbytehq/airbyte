/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.Database
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.Companion.`in`

class MssqlSourceDatatypeTest : AbstractMssqlSourceDatatypeTest() {
    override fun setupDatabase(): Database? {
        testdb = `in`(MsSQLTestDatabase.BaseImage.MSSQL_2022)
        return testdb!!.database
    }

    override val config: JsonNode
        get() = testdb!!.integrationTestConfigBuilder()
            .withoutSsl()
            .build()

    public override fun testCatalog(): Boolean {
        return true
    }
}
