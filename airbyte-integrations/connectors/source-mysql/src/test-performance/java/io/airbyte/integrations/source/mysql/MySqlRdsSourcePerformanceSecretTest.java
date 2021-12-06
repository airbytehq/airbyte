/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.standardtest.source.performancetest.AbstractSourcePerformanceTest;
import java.nio.file.Path;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;

public class MySqlRdsSourcePerformanceSecretTest extends AbstractSourcePerformanceTest {

  private JsonNode config;
  private static final String PERFORMANCE_SECRET_CREDS = "secrets/performance-config.json";

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
  protected void setupDatabase(String dbName) throws Exception {
    JsonNode plainConfig = Jsons.deserialize(IOs.readFile(Path.of(PERFORMANCE_SECRET_CREDS)));

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", plainConfig.get("host"))
        .put("port", plainConfig.get("port"))
        .put("database", dbName)
        .put("username", plainConfig.get("username"))
        .put("password", plainConfig.get("password"))
        .put("replication_method", plainConfig.get("replication_method"))
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:mysql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            dbName),
        "com.mysql.cj.jdbc.Driver",
        SQLDialect.MYSQL,
        "zeroDateTimeBehavior=convertToNull");

    // It disable strict mode in the DB and allows to insert specific values.
    // For example, it's possible to insert date with zero values "2021-00-00"
    database.query(ctx -> ctx.execute("SET @@sql_mode=''"));
    database.close();
  }

  @Test
  public void test100tables100recordsDb() throws Exception {
    int numberOfDummyRecords = 100; // 200 is near the max value for one shot in batching;
    int numberOfStreams = 100;
    String schemaName = "test100tables100recordsDb";

    setupDatabase(schemaName);

    performTest(schemaName, numberOfStreams, numberOfDummyRecords);
  }

  @Test
  public void test1000tables240columns200recordsDb() throws Exception {
    int numberOfDummyRecords = 200;
    int numberOfStreams = 1000;
    String schemaName = "test1000tables240columns200recordsDb";

    setupDatabase(schemaName);

    performTest(schemaName, numberOfStreams, numberOfDummyRecords);
  }

  @Test
  public void test5000tables240columns200recordsDb() throws Exception {
    int numberOfDummyRecords = 200;
    int numberOfStreams = 5000;
    String schemaName = "test5000tables240columns200recordsDb";

    setupDatabase(schemaName);

    performTest(schemaName, numberOfStreams, numberOfDummyRecords);
  }

  @Test
  public void testSmall1000tableswith10000recordsDb() throws Exception {
    int numberOfDummyRecords = 10001;
    int numberOfStreams = 1000;
    String schemaName = "newsmall1000tableswith10000rows";

    setupDatabase(schemaName);

    performTest(schemaName, numberOfStreams, numberOfDummyRecords);
  }

  @Test
  public void testInterim15tableswith50000recordsDb() throws Exception {
    int numberOfDummyRecords = 50010;
    int numberOfStreams = 15;
    String schemaName = "newinterim15tableswith50000records";

    setupDatabase(schemaName);

    performTest(schemaName, numberOfStreams, numberOfDummyRecords);
  }

  @Test
  public void testRegular25tables50000recordsDb() throws Exception {
    int numberOfDummyRecords = 50003;
    int numberOfStreams = 25;
    String schemaName = "newregular25tables50000records";

    setupDatabase(schemaName);

    performTest(schemaName, numberOfStreams, numberOfDummyRecords);
  }

}
