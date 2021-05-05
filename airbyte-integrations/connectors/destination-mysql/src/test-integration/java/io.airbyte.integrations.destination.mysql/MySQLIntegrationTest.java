package io.airbyte.integrations.destination.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.TestDestination;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;

public class MySQLIntegrationTest extends TestDestination {
  private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);

  private MySQLContainer<?> db;
  private ExtendedNameTransformer namingResolver = new MySQLNameTransformer();
  @Override
  protected String getImageName() {
    return "airbyte/destination-mysql:dev";
  }

  @Override
  protected JsonNode getConfig() {
    //root user is required cause by default the server value for local_infile is OFF and we need to turn it ON for loading data and the normal user doesn't have permission to switch it on
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", "root")
        .put("password", "test")
        .put("database", db.getDatabaseName())
        .put("port", db.getFirstMappedPort())
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", "wrong password")
        .put("database", db.getDatabaseName())
        .put("port", db.getFirstMappedPort())
        .build());
  }

  @Override
  protected String getDefaultSchema(JsonNode config) {
    if (config.get("database") == null) {
      return null;
    }
    return config.get("database").asText();
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv, String streamName,
      String namespace) throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(String tableName, String schemaName) throws SQLException {
    return Databases.createDatabase(
        db.getUsername(),
        db.getPassword(),
        String.format("jdbc:mysql://%s:%s/%s",
            db.getHost(),
            db.getFirstMappedPort(),
            db.getDatabaseName()),
        "com.mysql.cj.jdbc.Driver",
        SQLDialect.MYSQL).query(
        ctx -> ctx
            .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
            .stream()
            .map(r -> r.formatJSON(JSON_FORMAT))
            .map(Jsons::deserialize)
            .collect(Collectors.toList()));
  }


  @Override
  protected void setup(TestDestinationEnv testEnv) {
    db = new MySQLContainer<>("mysql:8.0");
    db.start();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }
}