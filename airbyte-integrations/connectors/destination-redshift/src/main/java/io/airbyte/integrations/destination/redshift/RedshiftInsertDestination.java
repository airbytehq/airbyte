/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftInsertDestination extends AbstractJdbcDestination  {

  private static final String DRIVER_CLASS = "com.amazon.redshift.jdbc.Driver";
  private static final String USERNAME = "username";
  private static final String PASSWORD = "password";
  private static final String SCHEMA = "schema";
  private static final String JDBC_URL = "jdbc_url";

  public RedshiftInsertDestination(final RedshiftDataTmpTableMode redshiftDataTmpTableMode) {
    super(DRIVER_CLASS, new RedshiftSQLNameTransformer(), new RedshiftSqlOperations(redshiftDataTmpTableMode));
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode redshiftConfig) {
    return getJdbcConfig(redshiftConfig);
  }

  @Override
  public JdbcDatabase getDatabase(final JsonNode config) {
    return getJdbcDatabase(config);
  }

  private static void addSsl(final List<String> additionalProperties) {
    additionalProperties.add("ssl=true");
    additionalProperties.add("sslfactory=com.amazon.redshift.ssl.NonValidatingFactory");
  }

  public static JdbcDatabase getJdbcDatabase(final JsonNode config) {
    final List<String> additionalProperties = new ArrayList<>();
    final var jdbcConfig = RedshiftInsertDestination.getJdbcConfig(config);
    addSsl(additionalProperties);
    return Databases.createJdbcDatabase(
        jdbcConfig.get(USERNAME).asText(),
        jdbcConfig.has(PASSWORD) ? jdbcConfig.get(PASSWORD).asText() : null,
        jdbcConfig.get(JDBC_URL).asText(),
        RedshiftInsertDestination.DRIVER_CLASS,
        String.join(";", additionalProperties));
  }

  public static JsonNode getJdbcConfig(final JsonNode redshiftConfig) {
    final String schema = Optional.ofNullable(redshiftConfig.get(SCHEMA)).map(JsonNode::asText).orElse("public");

    return Jsons.jsonNode(ImmutableMap.builder()
        .put(USERNAME, redshiftConfig.get(USERNAME).asText())
        .put(PASSWORD, redshiftConfig.get(PASSWORD).asText())
        .put(JDBC_URL, String.format("jdbc:redshift://%s:%s/%s",
            redshiftConfig.get("host").asText(),
            redshiftConfig.get("port").asText(),
            redshiftConfig.get("database").asText()))
        .put(SCHEMA, schema)
        .build());
  }
}
