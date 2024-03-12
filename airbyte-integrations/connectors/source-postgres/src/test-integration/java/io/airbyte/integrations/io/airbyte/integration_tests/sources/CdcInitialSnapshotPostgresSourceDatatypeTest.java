/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.JsonSchemaType;

public class CdcInitialSnapshotPostgresSourceDatatypeTest extends AbstractPostgresSourceDatatypeTest {

  private static final String SCHEMA_NAME = "test";

  @Override
  protected Database setupDatabase() throws Exception {
    testdb = PostgresTestDatabase.in(BaseImage.POSTGRES_16, ContainerModifier.CONF)
        .with("CREATE EXTENSION hstore;")
        .with("CREATE SCHEMA TEST;")
        .with("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');")
        .with("CREATE TYPE inventory_item AS (\n"
            + "    name            text,\n"
            + "    supplier_id     integer,\n"
            + "    price           numeric\n"
            + ");")
        .with("SET TIMEZONE TO 'MST'")
        .withReplicationSlot()
        .withPublicationForAllTables();
    return testdb.getDatabase();
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withSchemas(SCHEMA_NAME)
        .withoutSsl()
        .withCdcReplication()
        .build();
  }

  @Override
  protected void addHstoreTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("hstore")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("""
                             '"paperback" => "243","publisher" => "postgresqltutorial.com",
                             "language"  => "English","ISBN-13" => "978-1449370000",
                             "weight"    => "11.2 ounces"'
                             """, null)
            .addExpectedValues(
                //
                "\"weight\"=>\"11.2 ounces\", \"ISBN-13\"=>\"978-1449370000\", \"language\"=>\"English\", \"paperback\"=>\"243\", \"publisher\"=>\"postgresqltutorial.com\"",
                null)
            .build());
  }

}
