/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MariaDBContainer;
import org.testcontainers.utility.DockerImageName;

public class MariadbColumnstoreDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(MariadbColumnstoreDestinationAcceptanceTest.class);

  private final ExtendedNameTransformer namingResolver = new MariadbColumnstoreNameTransformer();

  private JsonNode configJson;

  private MariaDBContainer db;

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-mariadb-columnstore:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("database", db.getDatabaseName())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get("database") == null) {
      return null;
    }
    return config.get("database").asText();
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new MariaDbTestDataComparator();
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
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    JdbcDatabase database = getDatabase(getConfig());
    return database.unsafeQuery(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
        .collect(Collectors.toList());
  }

  private static JdbcDatabase getDatabase(final JsonNode config) {
    return Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.has("password") ? config.get("password").asText() : null,
        String.format("jdbc:mariadb://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        MariadbColumnstoreDestination.DRIVER_CLASS);
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    DockerImageName mcsImage = DockerImageName.parse("fengdi/columnstore:1.5.2").asCompatibleSubstituteFor("mariadb");
    db = new MariaDBContainer(mcsImage);
    db.start();

    String createUser = String.format("CREATE USER '%s'@'%%' IDENTIFIED BY '%s';", db.getUsername(), db.getPassword());
    String grantAll = String.format("GRANT ALL PRIVILEGES ON *.* TO '%s'@'%%' IDENTIFIED BY '%s';", db.getUsername(), db.getPassword());
    String createDb = String.format("CREATE DATABASE %s DEFAULT CHARSET = utf8;", db.getDatabaseName());
    db.execInContainer("mariadb", "-e", createUser + grantAll + createDb);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

}
