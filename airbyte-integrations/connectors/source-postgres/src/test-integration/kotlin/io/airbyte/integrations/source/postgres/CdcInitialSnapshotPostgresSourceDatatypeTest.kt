/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.Database

class CdcInitialSnapshotPostgresSourceDatatypeTest : AbstractPostgresSourceDatatypeTest() {
    @Throws(Exception::class)
    protected override fun setupDatabase(): Database {
        testdb =
            PostgresTestDatabase.`in`(
                    PostgresTestDatabase.BaseImage.POSTGRES_17,
                    PostgresTestDatabase.ContainerModifier.CONF
                )
                .with("CREATE EXTENSION hstore;")
                .with("CREATE SCHEMA $SCHEMA_NAME;")
                .with("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');")
                .with(
                    ("CREATE TYPE inventory_item AS (\n" +
                        "    name            text,\n" +
                        "    supplier_id     integer,\n" +
                        "    price           numeric\n" +
                        ");"),
                )
                .with("SET TIMEZONE TO 'MST'")
                .withReplicationSlot()
                .withPublicationForAllTables()
        return testdb.database
    }

    override val config: JsonNode
        get() =
            testdb
                .integrationTestConfigBuilder()
                .withSchemas(SCHEMA_NAME)
                .withoutSsl()
                .withCdcReplication()
                .build()
}
