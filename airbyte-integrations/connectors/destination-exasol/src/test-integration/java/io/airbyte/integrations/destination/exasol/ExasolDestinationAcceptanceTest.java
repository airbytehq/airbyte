/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import io.airbyte.integrations.util.HostPortResolver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ExasolDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(ExasolDestinationAcceptanceTest.class);

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private JsonNode configJson;

  @Override
  protected String getImageName() {
    return "airbyte/destination-exasol:dev";
  }

  @Override
  protected JsonNode getConfig() {

    return Jsons.jsonNode(ImmutableMap.builder()
            .put("connectionstring","172.17.0.2/60E5A89BE78537903378635DD996657676920AA87B4F6D99ABCA11748739C216:8563")
            .put(JdbcUtils.USERNAME_KEY, "sys")
            .put(JdbcUtils.PASSWORD_KEY, "exasol")
            .put(JdbcUtils.SCHEMA_KEY, "TEST")
            .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
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
    final JdbcDatabase jdbcDB = getDatabase(getConfig());
    final String query = String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    return jdbcDB.queryJsons(query);
  }

  private static JdbcDatabase getDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(
            DataSourceFactory.create(
                    config.get(JdbcUtils.USERNAME_KEY).asText(),
                    config.has(JdbcUtils.PASSWORD_KEY) ? config.get(JdbcUtils.PASSWORD_KEY).asText() : null,
                    ExasolDestination.DRIVER_CLASS,
                    String.format(DatabaseDriver.EXASOL.getUrlFormatString(), config.get("connectionstring").asText()))
    );
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
