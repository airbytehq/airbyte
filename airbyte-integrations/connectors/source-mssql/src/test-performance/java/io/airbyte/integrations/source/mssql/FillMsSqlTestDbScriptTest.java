/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.cdk.integrations.standardtest.source.performancetest.AbstractSourceFillDbWithTestData;
import io.airbyte.commons.json.Jsons;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.junit.jupiter.params.provider.Arguments;

public class FillMsSqlTestDbScriptTest extends AbstractSourceFillDbWithTestData {

  private JsonNode config;
  private DSLContext dslContext;

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {}

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql:dev";
  }

  @Override
  protected Database setupDatabase(final String dbName) {
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "your_host")
        .put(JdbcUtils.PORT_KEY, 1433)
        .put(JdbcUtils.DATABASE_KEY, dbName) // set your db name
        .put(JdbcUtils.USERNAME_KEY, "your_username")
        .put(JdbcUtils.PASSWORD_KEY, "your_pass")
        .put("replication_method", replicationMethod)
        .build());

    dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            dbName),
        null);

    return new Database(dslContext);
  }

  /**
   * This is a data provider for fill DB script,, Each argument's group would be ran as a separate
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
    return Stream.of(Arguments.of("your_db_name", "dbo", 100, 2, 240, 1000) // "dbo" is a default schema name in MsSQl DB
    );
  }

}
