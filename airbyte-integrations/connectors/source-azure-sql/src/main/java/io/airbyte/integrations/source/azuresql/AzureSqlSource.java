/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azuresql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.sql.JDBCType;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureSqlSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureSqlSource.class);

  static private String URL_STRING = "jdbc:sqlserver://kimerinnserver.database.windows.net:1433;database=test;encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;";
  static private String USER= "kimerinn@kimerinnserver";
  static final String DRIVER_CLASS = DatabaseDriver.MSSQLSERVER.getDriverClassName();
  public static final String MSSQL_CDC_OFFSET = "mssql_cdc_offset";
  public static final String MSSQL_DB_HISTORY = "mssql_db_history";
  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final String JDBC_URL_PARAMS_KEY = "jdbc_url_params";
  public static final List<String> HOST_KEY = List.of("host");
  public static final List<String> PORT_KEY = List.of("port");
  private static final String HIERARCHYID = "hierarchyid";

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new AzureSqlSource(), HOST_KEY, PORT_KEY);
  }

  AzureSqlSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new AzureSqlSourceOperations());
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode azureSqlConfig) {
    final List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(
        String.format("jdbc:sqlserver://%s.database.windows.net:1433;database=%s;encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;",
            azureSqlConfig.get("sqlserver").asText(),
            azureSqlConfig.get("database").asText()));

    if (!additionalParameters.isEmpty()) {
      jdbcUrl.append(String.join(";", additionalParameters));
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", azureSqlConfig.get("username").asText())
        .put("password", azureSqlConfig.get("password").asText())
        .put("jdbc_url", jdbcUrl.toString());

    if (azureSqlConfig.has(JDBC_URL_PARAMS_KEY)) {
      configBuilder.put("connection_properties", azureSqlConfig.get(JDBC_URL_PARAMS_KEY));
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA",
        "sys",
        "spt_fallback_db",
        "spt_monitor",
        "spt_values",
        "spt_fallback_usg",
        "MSreplication_options",
        "spt_fallback_dev",
        "cdc"); // is this actually ok? what if the user wants cdc schema for some reason?
  }

  public static void main(final String[] args) throws Exception {
    final AzureSqlSource source = new AzureSqlSource();
    LOGGER.info("starting source: {}", AzureSqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", AzureSqlSource.class);
  }
}
