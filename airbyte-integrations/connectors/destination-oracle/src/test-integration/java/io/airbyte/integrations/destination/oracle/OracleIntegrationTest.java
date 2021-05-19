/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.TestDestination;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.testcontainers.containers.OracleContainer;

public class OracleIntegrationTest extends TestDestination {

  private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);

  private static OracleContainer db;
  private ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();
  private JsonNode configWithoutDbName;
  private JsonNode config;

  @Override
  protected String getImageName() {
    return "airbyte/destination-oracle:dev";
  }

  private JsonNode getConfig(OracleContainer db) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", "testSchema")
        .put("sid", db.getSid())
        .build());
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", "wrong password")
        .put("schema", "public")
        .put("port", db.getFirstMappedPort())
        .put("sid", db.getSid())
        .put("ssl", false)
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv env, String streamName, String namespace) throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsBasicNormalization() {
    return false;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(TestDestinationEnv env, String streamName, String namespace)
      throws Exception {
    String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  @Override
  protected List<String> resolveIdentifier(String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
      result.add(resolved.toUpperCase());
    }
    return result;
  }

  private List<JsonNode> retrieveRecordsFromTable(String tableName, String schemaName) throws SQLException {
    return Databases.createSqlServerDatabase(db.getUsername(), db.getPassword(),
        db.getJdbcUrl()).query(
            ctx -> {
              ctx.fetch(String.format("USE %s;", config.get("database")));
              return ctx
                  .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                  .stream()
                  .map(r -> r.formatJSON(JSON_FORMAT))
                  .map(Jsons::deserialize)
                  .collect(Collectors.toList());
            });
  }

  @BeforeAll
  protected static void init() {
    db = new OracleContainer("epiclabs/docker-oracle-xe-11g");
    db.start();
  }

  private static Database getDatabase(JsonNode config) {
    // todo (cgardens) - rework this abstraction so that we do not have to pass a null into the
    // constructor. at least explicitly handle it, even if the impl doesn't change.
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:oracle:thin:@//%s:%s/%s",
                config.get("host").asText(),
                config.get("port").asText(),
                config.get("sid").asText()),
        "oracle.jdbc.driver.OracleDriver",
        null);
  }

  // how to interact with the mssql test container manually.
  // 1. exec into mssql container (not the test container container)
  // 2. /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P "A_Str0ng_Required_Password"
  @Override
  protected void setup(TestDestinationEnv testEnv) throws SQLException {
    configWithoutDbName = getConfig(db);
    final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    final Database database = getDatabase(configWithoutDbName);
    database.query(ctx -> {
      ctx.execute("declare c int; begin select count(*) into c from user_tables where upper(table_name) = upper('id_and_name'); if c = 1 then execute immediate 'drop table id_and_name'; end if; end;");
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER NOT NULL, name VARCHAR(200), born TIMESTAMP WITH TIME ZONE)");
      ctx.fetch(
          "INSERT ALL INTO id_and_name (id, name, born) VALUES (1,'picard', TIMESTAMP '2124-03-04 01:01:01') INTO id_and_name (id, name, born) VALUES  (2, 'crusher', TIMESTAMP '2124-03-04 01:01:01') INTO id_and_name (id, name, born) VALUES (3, 'vash', TIMESTAMP '2124-03-04 01:01:01') SELECT 1 FROM DUAL");
      return null;
    });

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put("database", dbName);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {}

  @AfterAll
  static void cleanUp() {
    db.stop();
    db.close();
  }

}
