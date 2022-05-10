/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.standardtest.source.performancetest.AbstractSourceFillDbWithTestData;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.params.provider.Arguments;

public class FillPostgresTestDbScriptTest extends AbstractSourceFillDbWithTestData {

  private JsonNode config;

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {}

  @Override
  protected String getImageName() {
    return "airbyte/source-postgres:dev";
  }

  @Override
  protected Database setupDatabase(final String dbName) throws Exception {
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", "your_host")
        .put("port", 5432)
        .put("database", dbName)
        .put("username", "your_username")
        .put("password", "your_pass")
        .put("replication_method", replicationMethod)
        .build());

    final DSLContext dslContext = DSLContextFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("database").asText()), SQLDialect.POSTGRES);
    final Database database = new Database(dslContext);

    return database;
  }

  /**
   * This is a data provider for fill DB script, Each argument's group would be ran as a separate
   * test. 1st arg - a name of DB that will be used in jdbc connection string. 2nd arg - a schemaName
   * that will be ised as a NameSpace in Configured Airbyte Catalog. 3rd arg - a number of expected
   * records retrieved in each stream. 4th arg - a number of messages batches
   * (numberOfMessages*numberOfBatches, ex. 100*2=200 messages in total in each stream) 5th arg - a
   * number of columns in each stream\table that will be use for Airbyte Cataloq configuration 6th arg
   * - a number of streams to read in configured airbyte Catalog. Each stream\table in DB should be
   * names like "test_0", "test_1",..., test_n.
   */
  @Override
  protected Stream<Arguments> provideParameters() {
    return Stream.of(Arguments.of("postgres", "\"your_schema_name\"", 100, 2, 240, 1000));
  }

}
