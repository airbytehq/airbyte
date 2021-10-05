/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
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
