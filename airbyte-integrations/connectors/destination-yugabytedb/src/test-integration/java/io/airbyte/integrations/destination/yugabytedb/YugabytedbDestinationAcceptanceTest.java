/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yugabytedb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.json.Jsons;
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

  private final StandardNameTransformer namingResolver = new StandardNameTransformer();

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
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
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
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    database.execute(connection -> {
      final var statement = connection.createStatement();
      cleanupTables.forEach(tb -> {
        try {
          statement.execute("DROP TABLE " + tb + ";");
        } catch (final SQLException e) {
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
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws SQLException {

    final String tableName = namingResolver.getRawTableName(streamName);
    final String schemaName = namingResolver.getNamespace(namespace);
    cleanupTables.add(schemaName + "." + tableName);
    return retrieveRecordsFromTable(tableName, schemaName);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName)
      throws SQLException {

    return database.bufferedResultSetQuery(
        connection -> {
          final var statement = connection.createStatement();
          return statement.executeQuery(
              String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
                  JavaBaseConstants.COLUMN_NAME_EMITTED_AT));
        },
        rs -> Jsons.deserialize(rs.getString(JavaBaseConstants.COLUMN_NAME_DATA)));
  }

}
