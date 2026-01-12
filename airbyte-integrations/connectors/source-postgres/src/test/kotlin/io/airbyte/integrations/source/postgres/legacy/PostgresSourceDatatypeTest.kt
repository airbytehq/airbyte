/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.Database
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils.MODE_KEY
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase
import java.sql.SQLException

class PostgresSourceDatatypeTest : AbstractPostgresSourceDatatypeTest() {
    @Throws(SQLException::class)
    protected override fun setupDatabase(): Database {
        testdb =
            PostgresTestDatabase.`in`(
                    PostgresTestDatabase.BaseImage.POSTGRES_17,
                    PostgresTestDatabase.ContainerModifier.CONF
                )
                .with("CREATE SCHEMA %S;", SCHEMA_NAME)
                .with("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');")
                .with(
                    "CREATE TYPE inventory_item AS (name text, supplier_id integer, price numeric);"
                ) // In one of the test case, we have some money values with currency symbol.
                // Postgres can only
                // understand those money values if the symbol corresponds to the monetary locale
                // setting. For
                // example,
                // if the locale is 'en_GB', '£100' is valid, but '$100' is not. So setting the
                // monetary locate is
                // necessary here to make sure the unit test can pass, no matter what the locale the
                // runner VM has.
                .with(
                    "SET lc_monetary TO 'en_US.utf8';"
                ) // Set up a fixed timezone here so that timetz and timestamptz always have the
                // same time zone
                // wherever the tests are running on.
                .with("SET TIMEZONE TO 'MST'")
                .with("CREATE EXTENSION hstore;")
        return testdb.database
    }

    @get:Throws(Exception::class)
    override val config: JsonNode
        get() =
            testdb
                .integrationTestConfigBuilder()
                .withSsl(mutableMapOf(MODE_KEY to "disable"))
                .withStandardReplication()
                .withSchemas(SCHEMA_NAME)
                .build()
}
