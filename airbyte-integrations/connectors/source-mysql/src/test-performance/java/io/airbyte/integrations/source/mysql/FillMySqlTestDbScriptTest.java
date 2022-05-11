/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.source.mysql.MySqlSource.ReplicationMethod;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.standardtest.source.performancetest.AbstractSourceFillDbWithTestData;
import java.util.Map;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.junit.jupiter.params.provider.Arguments;

public class FillMySqlTestDbScriptTest extends AbstractSourceFillDbWithTestData {

  private JsonNode config;

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {}

  @Override
  protected String getImageName() {
    return "airbyte/source-mysql:dev";
  }

  @Override
  protected Database setupDatabase(final String dbName) throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", "your_host")
        .put("port", 3306)
        .put("database", dbName) // set your db name
        .put("username", "your_username")
        .put("password", "your_pass")
        .put("replication_method", ReplicationMethod.STANDARD)
        .build());

    final Database database = new Database(
        DSLContextFactory.create(
            config.get("username").asText(),
            config.get("password").asText(),
            DatabaseDriver.MYSQL.getDriverClassName(),
            String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
                config.get("host").asText(),
                config.get("port").asInt(),
                config.get("database").asText()),
            SQLDialect.MYSQL,
            Map.of("zeroDateTimeBehavior", "convertToNull"))
    );

    // It disable strict mode in the DB and allows to insert specific values.
    // For example, it's possible to insert date with zero values "2021-00-00"
    database.query(ctx -> ctx.execute("SET @@sql_mode=''"));

    return database;
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
    // for MySQL DB name ans schema name would be the same
    return Stream.of(Arguments.of("your_db_name", "your_schema_name", 100, 2, 240, 1000));
  }

}
