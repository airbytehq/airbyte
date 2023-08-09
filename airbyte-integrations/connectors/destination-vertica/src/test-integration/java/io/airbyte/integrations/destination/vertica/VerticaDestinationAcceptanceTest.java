/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.vertica;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class VerticaDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(VerticaDestinationAcceptanceTest.class);
  private static VerticaContainer db;
  private final StandardNameTransformer namingResolver = new StandardNameTransformer();
  private JsonNode configJson;
  private DSLContext dslContext;

  @Override
  protected String getImageName() {
    return "airbyte/destination-vertica:dev";
  }

  @Override
  protected JsonNode getConfig() {
    // TODO: Generate the configuration JSON file to be used for running the destination during the test
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "140.236.88.151")
        .put(JdbcUtils.USERNAME_KEY, "airbyte")
        .put(JdbcUtils.PASSWORD_KEY, "airbyte123")
        .put(JdbcUtils.SCHEMA_KEY, "airbyte")
        .put(JdbcUtils.PORT_KEY, 5433)
        .put(JdbcUtils.DATABASE_KEY, "airbyte")
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    // TODO return an invalid config which, when used to run the connector's check connection operation,
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getContainerInfo().getNetworkSettings().getIpAddress())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, "wrong password")
        .put(JdbcUtils.SCHEMA_KEY, "public")
        .put(JdbcUtils.PORT_KEY, db.getVerticaPort())
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    try (final DSLContext dslContext = DSLContextFactory.create(
        "airbyte",
        "airbyte123",
        db.getDriverClassName(),
        String.format(DatabaseDriver.VERTICA.getUrlFormatString(),
            "140.236.88.151",
            5433,
            "airbyte"),
        SQLDialect.DEFAULT)) {
      final List<JsonNode> recordsFromTable = new Database(dslContext).query(
          ctx -> ctx
              .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
                  JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
              .stream()
              .map(this::getJsonFromRecord)
              .collect(Collectors.toList()));
      return recordsFromTable;
    }
  }

  @Override
  @Test
  public void testLineBreakCharacters() {
    // overrides test with a no-op until we handle full UTF-8 in the destination
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws IOException, SQLException {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  @BeforeAll
  protected static void init() {
    db = new VerticaContainer();
    db.start();
  }

  @AfterAll
  static void cleanUp() {
    db.stop();
    db.close();
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    // TODO Implement this method to run any setup actions needed before every test case

  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    // TODO Implement this method to run any cleanup actions needed after every test case
  }

}
