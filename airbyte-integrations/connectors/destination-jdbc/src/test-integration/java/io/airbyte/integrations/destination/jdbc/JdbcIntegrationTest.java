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

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.ExtendedSQLNaming;
import io.airbyte.integrations.standardtest.destination.TestDestination;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.testcontainers.containers.PostgreSQLContainer;

public class JdbcIntegrationTest extends TestDestination {

  private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);

  private static final String RAW_DATA_COLUMN = "data";
  private PostgreSQLContainer<?> db;
  private final ExtendedSQLNaming namingResolver = new ExtendedSQLNaming();

  @Override
  protected String getImageName() {
    return "airbyte/destination-jdbc:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", "public")
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            db.getHost(),
            db.getFirstMappedPort(),
            db.getDatabaseName()))
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", db.getUsername())
        .put("password", "wrong password")
        .put("schema", "public")
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            db.getHost(),
            db.getFirstMappedPort(),
            db.getDatabaseName()))
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv env, String streamName) throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName))
        .stream()
        .map(r -> Jsons.deserialize(r.get(RAW_DATA_COLUMN).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsBasicNormalization() {
    return false;
  }

  @Override
  protected boolean implementsIncremental() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(TestDestinationEnv env, String streamName)
      throws Exception {
    String tableName = namingResolver.getIdentifier(streamName);
    if (!tableName.startsWith("\"")) {
      // Currently, Normalization always quote tables identifiers
      tableName = "\"" + tableName + "\"";
    }
    return retrieveRecordsFromTable(tableName);
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

  private List<JsonNode> retrieveRecordsFromTable(String tableName) throws SQLException {
    return Databases.createPostgresDatabase(db.getUsername(), db.getPassword(),
        db.getJdbcUrl()).query(
            ctx -> ctx
                .fetch(String.format("SELECT * FROM %s ORDER BY emitted_at ASC;", tableName))
                .stream()
                .map(r -> r.formatJSON(JSON_FORMAT))
                .map(Jsons::deserialize)
                .collect(Collectors.toList()));
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    db = new PostgreSQLContainer<>("postgres:13-alpine");
    db.start();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

}
