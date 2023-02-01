/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yugabytedb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.TestInstance;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class YugabytedbDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(YugabytedbDestinationAcceptanceTest.class);

  private YugabytedbContainerInitializr.YugabytedbContainer yugabytedbContainer;

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private JsonNode jsonConfig;

  private JdbcDatabase database;

  private static final Set<String> cleanupTables = new HashSet<>();

  @BeforeAll
  void initContainer() {
    yugabytedbContainer = YugabytedbContainerInitializr.initContainer();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-yugabytedb:dev";
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    jsonConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", yugabytedbContainer.getHost())
        .put("port", yugabytedbContainer.getMappedPort(5433))
        .put("database", yugabytedbContainer.getDatabaseName())
        .put("username", yugabytedbContainer.getUsername())
        .put("password", yugabytedbContainer.getPassword())
        .put("schema", "public")
        .build());

    database = new DefaultJdbcDatabase(YugabyteDataSource.getInstance(
        yugabytedbContainer.getHost(),
        yugabytedbContainer.getMappedPort(5433),
        yugabytedbContainer.getDatabaseName(),
        yugabytedbContainer.getUsername(),
        yugabytedbContainer.getPassword()));

  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    database.execute(connection -> {
      var statement = connection.createStatement();
      cleanupTables.forEach(tb -> {
        try {
          statement.execute("DROP TABLE " + tb + ";");
        } catch (SQLException e) {
          throw new RuntimeException(e);
        }
      });
    });
    cleanupTables.clear();
  }

  @Override
  protected JsonNode getConfig() {
    return jsonConfig;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", yugabytedbContainer.getHost())
        .put("port", yugabytedbContainer.getMappedPort(5433))
        .put("database", yugabytedbContainer.getDatabaseName())
        .put("username", "usr")
        .put("password", "pw")
        .put("schema", "public")
        .build());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws SQLException {

    String tableName = namingResolver.getRawTableName(streamName);
    String schemaName = namingResolver.getNamespace(namespace);
    cleanupTables.add(schemaName + "." + tableName);
    return retrieveRecordsFromTable(tableName, schemaName);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName)
      throws SQLException {

    return database.bufferedResultSetQuery(
        connection -> {
          var statement = connection.createStatement();
          return statement.executeQuery(
              String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
                  JavaBaseConstants.COLUMN_NAME_EMITTED_AT));
        },
        rs -> Jsons.deserialize(rs.getString(JavaBaseConstants.COLUMN_NAME_DATA)));
  }

}
