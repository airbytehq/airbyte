/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import static io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.util.ApmTraceUtils;
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSource extends AbstractJdbcSource<JDBCType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSource.class);
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;

  public static final String DRIVER_CLASS = DatabaseDriver.REDSHIFT.getDriverClassName();

  @VisibleForTesting
  static final String AUTHENTICATION_FAILED_MESSAGE =
      "Authentication to Redshift failed. Update the username and password in the source configuration.";
  // SQLSTATE class 28 is "Invalid Authorization Specification" (e.g. 28000, 28P01).
  private static final String INVALID_AUTHORIZATION_SQL_STATE_CLASS = "28";
  private List<String> schemas;

  // todo (cgardens) - clean up passing the dialect as null versus explicitly adding the case to the
  // constructor.
  public RedshiftSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new RedshiftSourceOperations());
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode redshiftConfig) {
    final List<String> additionalProperties = new ArrayList<>();
    final ImmutableMap.Builder<Object, Object> builder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, redshiftConfig.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.PASSWORD_KEY, redshiftConfig.get(JdbcUtils.PASSWORD_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, getJdbcUrl(redshiftConfig));

    if (redshiftConfig.has(JdbcUtils.SCHEMAS_KEY) && redshiftConfig.get(JdbcUtils.SCHEMAS_KEY).isArray()) {
      schemas = new ArrayList<>();
      for (final JsonNode schema : redshiftConfig.get(JdbcUtils.SCHEMAS_KEY)) {
        schemas.add(schema.asText());
      }

      if (schemas != null && !schemas.isEmpty()) {
        additionalProperties.add("currentSchema=" + String.join(",", schemas));
      }
    }

    addSsl(additionalProperties);

    if (redshiftConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null && !redshiftConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty()) {
      additionalProperties.addAll(List.of(redshiftConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().split("&")));
    }

    builder.put(JdbcUtils.CONNECTION_PROPERTIES_KEY, String.join("&", additionalProperties));

    return Jsons.jsonNode(builder
        .build());
  }

  public static String getJdbcUrl(final JsonNode redshiftConfig) {
    return String.format(DatabaseDriver.REDSHIFT.getUrlFormatString(),
        redshiftConfig.get(JdbcUtils.HOST_KEY).asText(),
        redshiftConfig.get(JdbcUtils.PORT_KEY).asInt(),
        redshiftConfig.get(JdbcUtils.DATABASE_KEY).asText());
  }

  private void addSsl(final List<String> additionalProperties) {
    additionalProperties.add("ssl=true");
    additionalProperties.add("sslfactory=com.amazon.redshift.ssl.NonValidatingFactory");
  }

  @Override
  public JdbcDatabase createDatabase(final JsonNode sourceConfig, final String delimiter) throws SQLException {
    try {
      return super.createDatabase(sourceConfig, delimiter);
    } catch (final ConnectionErrorException e) {
      throw translateConnectionError(e);
    }
  }

  @VisibleForTesting
  static RuntimeException translateConnectionError(final ConnectionErrorException e) {
    final String stateCode = e.getStateCode();
    if (stateCode != null && stateCode.startsWith(INVALID_AUTHORIZATION_SQL_STATE_CLASS)) {
      return new ConfigErrorException(AUTHENTICATION_FAILED_MESSAGE, e);
    }
    return e;
  }

  /**
   * Mirrors {@code AbstractDbSource#check}, but also surfaces {@link ConfigErrorException}s raised by
   * {@link #createDatabase} as config errors with their display message.
   */
  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    try {
      final JdbcDatabase database = createDatabase(config);
      for (final CheckedConsumer<JdbcDatabase, Exception> checkOperation : getCheckOperations(config)) {
        checkOperation.accept(database);
      }
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final ConfigErrorException e) {
      ApmTraceUtils.addExceptionToTrace(e);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, e.getDisplayMessage());
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(e.getDisplayMessage());
    } catch (final ConnectionErrorException e) {
      ApmTraceUtils.addExceptionToTrace(e);
      final String message = getErrorMessage(e.getStateCode(), e.getErrorCode(), e.getExceptionMessage(), e);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(message);
    } catch (final Exception e) {
      ApmTraceUtils.addExceptionToTrace(e);
      LOGGER.info("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(String.format(ConnectorExceptionUtil.COMMON_EXCEPTION_MESSAGE_TEMPLATE, e.getMessage()));
    } finally {
      close();
    }
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(final JdbcDatabase database) throws Exception {
    if (schemas != null && !schemas.isEmpty()) {
      // process explicitly selected (from UI) schemas
      final List<TableInfo<CommonField<JDBCType>>> internals = new ArrayList<>();
      for (final String schema : schemas) {
        LOGGER.debug("Discovering schema: {}", schema);
        internals.addAll(super.discoverInternal(database, schema));
      }
      for (final TableInfo<CommonField<JDBCType>> info : internals) {
        LOGGER.debug("Found table (schema: {}): {}", info.getNameSpace(), info.getName());
      }
      return internals;
    } else {
      LOGGER.info("No schemas explicitly set on UI to process, so will process all of existing schemas in DB");
      return super.discoverInternal(database);
    }
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of("information_schema", "pg_catalog", "pg_internal", "catalog_history");
  }

  @Override
  @SuppressWarnings("unchecked")
  public Set<JdbcPrivilegeDto> getPrivilegesTableForCurrentUser(final JdbcDatabase database, final String schema) throws SQLException {
    return new HashSet<>(database.bufferedResultSetQuery(
        connection -> {
          connection.setAutoCommit(true);
          final PreparedStatement ps = connection.prepareStatement(
              "SELECT schemaname, tablename "
                  + "FROM   pg_tables "
                  + "WHERE  has_table_privilege(schemaname||'.'||tablename, 'select') = true AND schemaname = ?;");
          ps.setString(1, schema);
          return ps.executeQuery();
        },
        resultSet -> {
          final JsonNode json = sourceOperations.rowToJson(resultSet);
          return JdbcPrivilegeDto.builder()
              .schemaName(json.get("schemaname").asText())
              .tableName(json.get("tablename").asText())
              .build();
        }));
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new RedshiftSource();
    LOGGER.info("starting source: {}", RedshiftSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", RedshiftSource.class);
  }

}
