/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import static java.util.stream.Collectors.toSet;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSource.class);
  public static final String DRIVER_CLASS = "com.amazon.redshift.jdbc.Driver";

  // todo (cgardens) - clean up passing the dialect as null versus explicitly adding the case to the
  // constructor.
  public RedshiftSource() {
    super(DRIVER_CLASS, new RedshiftJdbcStreamingQueryConfiguration(), JdbcUtils.getDefaultSourceOperations());
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode redshiftConfig) {
    final List<String> additionalProperties = new ArrayList<>();
    final ImmutableMap.Builder<Object, Object> builder = ImmutableMap.builder()
        .put("username", redshiftConfig.get("username").asText())
        .put("password", redshiftConfig.get("password").asText())
        .put("jdbc_url", String.format("jdbc:redshift://%s:%s/%s",
            redshiftConfig.get("host").asText(),
            redshiftConfig.get("port").asText(),
            redshiftConfig.get("database").asText()));
    addSsl(additionalProperties);
    builder.put("connection_properties", String.join(";", additionalProperties));

    return Jsons.jsonNode(builder
        .build());
  }

  private void addSsl(final List<String> additionalProperties) {
    additionalProperties.add("ssl=true");
    additionalProperties.add("sslfactory=com.amazon.redshift.ssl.NonValidatingFactory");
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of("information_schema", "pg_catalog", "pg_internal", "catalog_history");
  }

 @Override
  public Set<JdbcPrivilegeDto> getPrivilegesTableForCurrentUser(final JdbcDatabase database, final String schema) throws SQLException {
    return database.query(connection -> {
      final PreparedStatement ps = connection.prepareStatement(
          "SELECT DISTINCT table_catalog, table_schema, table_name, privilege_type\n"
              + "FROM   information_schema.table_privileges\n"
              + "WHERE  grantee = ? AND privilege_type = 'SELECT'");
      ps.setString(1, database.getDatabaseConfig().get("username").asText());
      return ps;
    }, sourceOperations::rowToJson)
        .collect(toSet())
        .stream()
        .map(e -> JdbcPrivilegeDto.builder()
            .schemaName(e.get("table_schema").asText())
            .tableName(e.get("table_name").asText())
            .build())
        .collect(toSet());
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new RedshiftSource();
    LOGGER.info("starting source: {}", RedshiftSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", RedshiftSource.class);
  }

}
