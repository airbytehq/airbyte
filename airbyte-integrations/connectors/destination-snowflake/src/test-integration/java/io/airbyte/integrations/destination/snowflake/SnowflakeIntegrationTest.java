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

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.NamingHelper;
import io.airbyte.integrations.standardtest.destination.TestDestination;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;

public class SnowflakeIntegrationTest extends TestDestination {

  private String namespace;
  private JsonNode config;
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  @Override
  protected String getNamespace() {
    return namespace;
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-snowflake:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  private static JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("password", "wrong password");
    return invalidConfig;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv env, String streamName) throws Exception {
    streamName = NamingHelper.getTmpSchemaName(namingResolver, getNamespace()) + "." + namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(streamName)
        .stream()
        .map(j -> Jsons.deserialize(j.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsBasicNormalization() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(TestDestinationEnv testEnv, String streamName) throws Exception {
    String schemaName = namingResolver.getIdentifier(getNamespace());
    String tableName = namingResolver.getIdentifier(streamName);
    // Currently, Normalization always quote tables identifiers, see quoting rules
    // in airbyte-integrations/bases/base-normalization/dbt-project-template/dbt_project.yml
    if (!schemaName.startsWith("\""))
      schemaName = "\"" + schemaName + "\"";
    if (!tableName.startsWith("\""))
      tableName = "\"" + tableName + "\"";
    return retrieveRecordsFromTable(schemaName + "." + tableName);
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

  private List<JsonNode> retrieveRecordsFromTable(String tableName) throws SQLException, InterruptedException {
    return SnowflakeDatabase.getDatabase(getConfig()).bufferedResultSetQuery(
        connection -> connection.createStatement()
            .executeQuery(String.format("SELECT * FROM %s ORDER BY %s ASC;", tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT)),
        JdbcUtils::rowToJson);
  }

  // for each test we create a new schema in the database. run the test in there and then remove it.
  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    namespace = ("integration_test_" + RandomStringUtils.randomAlphanumeric(5));
    config = getStaticConfig();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    final String tmpSchema = NamingHelper.getTmpSchemaName(namingResolver, getNamespace());
    SnowflakeDatabase.getDatabase(config).execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE", tmpSchema));
    SnowflakeDatabase.getDatabase(config).execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE", getNamespace()));
  }

}
