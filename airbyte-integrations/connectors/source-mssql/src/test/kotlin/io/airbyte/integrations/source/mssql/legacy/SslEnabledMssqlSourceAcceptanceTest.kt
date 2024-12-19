/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.integrations.source.mssql.MsSQLContainerFactory
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase
import kotlin.test.Test

class SslEnabledMssqlSourceAcceptanceTest : MssqlSourceAcceptanceTest() {
    override val config: JsonNode
        get() = testdb!!.integrationTestConfigBuilder()
            .withEncrytedTrustServerCertificate()
            .build()

    override fun setupEnvironment(environment: TestDestinationEnv?) {
        val container = MsSQLContainerFactory().shared(MsSQLTestDatabase.BaseImage.MSSQL_2022.reference)
        testdb = MsSQLTestDatabase(container)
        testdb = testdb!!
            .withConnectionProperty("encrypt", "true")
            .withConnectionProperty("trustServerCertificate", "true")
            .withConnectionProperty("databaseName", testdb!!.databaseName)
            .initialized()
            .with("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));")
            .with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME2)
            .with(
                "INSERT INTO id_and_name (id, name, born) VALUES " +
                        "(1, 'picard', '2124-03-04T01:01:01Z'), " +
                        "(2, 'crusher', '2124-03-04T01:01:01Z'), " +
                        "(3, 'vash', '2124-03-04T01:01:01Z');"
            )
            .with("INSERT INTO %s.%s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato'), (4, 'Argo');", SCHEMA_NAME, STREAM_NAME2)
            .with("CREATE TABLE %s.%s (id INTEGER PRIMARY KEY, name VARCHAR(200), userid INTEGER DEFAULT NULL);", SCHEMA_NAME, STREAM_NAME3)
            .with("INSERT INTO %s.%s (id, name) VALUES (4,'voyager');", SCHEMA_NAME, STREAM_NAME3)
    }

    @Test
    override fun testIdenticalFullRefreshes() {
        super.testIdenticalFullRefreshes()
    }
}
