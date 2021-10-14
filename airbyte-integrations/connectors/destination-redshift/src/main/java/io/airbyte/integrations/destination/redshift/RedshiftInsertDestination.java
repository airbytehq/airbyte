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
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftInsertDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftDestination.class);

  public static final String DRIVER_CLASS = "com.amazon.redshift.jdbc.Driver";

  public RedshiftInsertDestination() {
    super(DRIVER_CLASS, new RedshiftSQLNameTransformer(), new RedshiftSqlOperations());
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode redshiftConfig) {
    return getJdbcConfig(redshiftConfig);
  }

  @Override
  public JdbcDatabase getDatabase(JsonNode config) {
    return getJdbcDatabase(config);
  }

  private static void readSsl(JsonNode redshiftConfig, List<String> additionalProperties) {
    boolean tls = redshiftConfig.has("tls") && redshiftConfig.get("tls").asBoolean(); // for backward compatibility
    if (!tls) {
      additionalProperties.add("ssl=false");
    } else {
      additionalProperties.add("ssl=true");
      additionalProperties.add("sslfactory=com.amazon.redshift.ssl.NonValidatingFactory");
    }
  }

  public static JdbcDatabase getJdbcDatabase(JsonNode config) {
    List<String> additionalProperties = new ArrayList<>();
    var jdbcConfig = RedshiftInsertDestination.getJdbcConfig(config);
    readSsl(config, additionalProperties);
    return Databases.createJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        RedshiftInsertDestination.DRIVER_CLASS,
        additionalProperties.isEmpty() ? "" : String.join(";", additionalProperties));
  }

  public static JsonNode getJdbcConfig(JsonNode redshiftConfig) {
    final String schema = Optional.ofNullable(redshiftConfig.get("schema")).map(JsonNode::asText).orElse("public");

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", redshiftConfig.get("username").asText())
        .put("password", redshiftConfig.get("password").asText())
        .put("jdbc_url", String.format("jdbc:redshift://%s:%s/%s",
            redshiftConfig.get("host").asText(),
            redshiftConfig.get("port").asText(),
            redshiftConfig.get("database").asText()))
        .put("schema", schema)
        .build());
  }

}
