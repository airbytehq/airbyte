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
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleIntegrationTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleIntegrationTest.class);
  private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);

  private static JsonNode baseConfig;
  private ExtendedNameTransformer namingResolver = new OracleNameTransformer();
  private static JsonNode config;

  public JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-oracle:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv env, String streamName, String namespace, JsonNode streamSchema) throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(OracleDestination.COLUMN_NAME_DATA.replace("\"", "")).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(TestDestinationEnv env, String streamName, String namespace)
      throws Exception {
    String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("password", "wrong password");
    return invalidConfig;
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
    List<org.jooq.Record> result = getDatabase()
        .query(ctx -> ctx.fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName, OracleDestination.COLUMN_NAME_EMITTED_AT))
            .stream()
            .collect(Collectors.toList()));
    return result
        .stream()
        .map(r -> r.formatJSON(JSON_FORMAT))
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

  private static Database getDatabase() {
    // todo (cgardens) - rework this abstraction so that we do not have to pass a null into the
    // constructor. at least explicitly handle it, even if the impl doesn't change.
    return Databases.createDatabase(
        baseConfig.get("username").asText(),
        baseConfig.get("password").asText(),
        String.format("jdbc:oracle:thin:@//%s:%s/%s",
            baseConfig.get("host").asText(),
            baseConfig.get("port").asText(),
            baseConfig.get("sid").asText()),
        "oracle.jdbc.driver.OracleDriver",
        null);
  }

  private List<String> allTables;

  private List<String> getAllTables(Database db) {
    try {
      return db.query(ctx -> ctx.fetch("select OWNER, TABLE_NAME from ALL_TABLES where upper(TABLESPACE_NAME) = 'USERS'")
          .stream()
          .map(r -> String.format("%s.%s", r.get("OWNER"), r.get("TABLE_NAME")))
          .collect(Collectors.toList()));
    } catch (SQLException e) {
      LOGGER.error("Error while cleaning up test.", e);
      return null;
    }
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws SQLException {
    // config = getConfig(db);
    baseConfig = getStaticConfig();
    config = Jsons.clone(baseConfig);
    final Database database = getDatabase();
    allTables = getAllTables(database);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    config = getStaticConfig();

    final Database database = getDatabase();
    var tables = getAllTables(database);
    try {
      for (String table : tables) {
        database.query(ctx -> {
          ctx.execute("drop table " + table);
          return null;
        });
      }
    } catch (SQLException e) {
      LOGGER.error("Error while cleaning up test.", e);
    }
  }

}
