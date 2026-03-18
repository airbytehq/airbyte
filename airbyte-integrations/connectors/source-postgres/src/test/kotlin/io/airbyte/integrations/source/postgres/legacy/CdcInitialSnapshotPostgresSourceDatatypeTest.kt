package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.Database
import io.airbyte.cdk.test.fixtures.legacy.TestDataHolder
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase
import io.airbyte.protocol.models.JsonSchemaType

class CdcInitialSnapshotPostgresSourceDatatypeTest : AbstractPostgresSourceDatatypeTest() {
    @Throws(Exception::class)
    protected override fun setupDatabase(): Database {
        testdb = PostgresTestDatabase.`in`(PostgresTestDatabase.BaseImage.POSTGRES_17, PostgresTestDatabase.ContainerModifier.CONF)
            .with("CREATE EXTENSION hstore;")
            .with("CREATE SCHEMA $SCHEMA_NAME;")
            .with("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');")
            .with(
                ("CREATE TYPE inventory_item AS (\n"
                    + "    name            text,\n"
                    + "    supplier_id     integer,\n"
                    + "    price           numeric\n"
                    + ");"),
            )
            .with("SET TIMEZONE TO 'MST'")
            .withReplicationSlot()
            .withPublicationForAllTables()
        return testdb.database
    }

    override val config: JsonNode
        get() = testdb.integrationTestConfigBuilder()
            .withSchemas(SCHEMA_NAME)
            .withoutSsl()
            .withCdcReplication()
            .build()

    override fun addHstoreTest() {
        addDataTypeTestData(
            TestDataHolder.builder()
                .sourceType("hstore")
                .airbyteType(JsonSchemaType.STRING)
                .addInsertValues(
                    """
                             '"paperback" => "243","publisher" => "postgresqltutorial.com",
                             "language"  => "English","ISBN-13" => "978-1449370000",
                             "weight"    => "11.2 ounces"'
                             
                             """.trimIndent(),
//                    null,
                )
                .addExpectedValues(
                    //
                    "\"weight\"=>\"11.2 ounces\", \"ISBN-13\"=>\"978-1449370000\", \"language\"=>\"English\", \"paperback\"=>\"243\", \"publisher\"=>\"postgresqltutorial.com\"",
//                    null,
                )
                .build(),
        )
    }
}
