/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.exceptions.DisplayErrorMessage;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.sql.SQLException;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractJdbcDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcDestination.class);

  private final String driverClass;
  private final NamingConventionTransformer namingResolver;
  private final SqlOperations sqlOperations;

  protected NamingConventionTransformer getNamingResolver() {
    return namingResolver;
  }

  protected SqlOperations getSqlOperations() {
    return sqlOperations;
  }

  public AbstractJdbcDestination(final String driverClass,
                                 final NamingConventionTransformer namingResolver,
                                 final SqlOperations sqlOperations) {
    this.driverClass = driverClass;
    this.namingResolver = namingResolver;
    this.sqlOperations = sqlOperations;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final DataSource dataSource = getDataSource(config);

    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final String outputSchema = namingResolver.getIdentifier(config.get(JdbcUtils.SCHEMA_KEY).asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, namingResolver, sqlOperations);
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final ConfigErrorException ex) {
      final String message = ex.getDisplayMessage();
      AirbyteTraceMessageUtility.emitConfigErrorTrace(ex, message);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(message);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  public static void attemptSQLCreateAndDropTableOperations(final String outputSchema,
                                                            final JdbcDatabase database,
                                                            final NamingConventionTransformer namingResolver,
                                                            final SqlOperations sqlOps)
      throws Exception {
    // verify we have write permissions on the target schema by creating a table with a random name,
    // then dropping that table
    try {
      // Get metadata from the database to see whether connection is possible
      database.bufferedResultSetQuery(conn -> conn.getMetaData().getCatalogs(), JdbcUtils.getDefaultSourceOperations()::rowToJson);

      // verify we have write permissions on the target schema by creating a table with a random name,
      // then dropping that table
      final String outputTableName = namingResolver.getIdentifier("_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", ""));
      sqlOps.createSchemaIfNotExists(database, outputSchema);
      sqlOps.createTableIfNotExists(database, outputSchema, outputTableName);
      sqlOps.dropTableIfExists(database, outputSchema, outputTableName);
    } catch (final SQLException e) {
      if (Objects.isNull(e.getCause()) || !(e.getCause() instanceof SQLException)) {
        throw new ConfigErrorException(DisplayErrorMessage.getErrorMessage(e.getSQLState(), e.getErrorCode(), e.getMessage(), e), e);
      } else {
        final SQLException cause = (SQLException) e.getCause();
        throw new ConfigErrorException(DisplayErrorMessage.getErrorMessage(e.getSQLState(), cause.getErrorCode(), cause.getMessage(), e), e);
      }
    } catch (final Exception e) {
      throw new Exception(e);
    }
  }

  protected DataSource getDataSource(final JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);
    return DataSourceFactory.create(
        jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        driverClass,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        getConnectionProperties(config));
  }

  protected JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  protected Map<String, String> getConnectionProperties(final JsonNode config) {
    final Map<String, String> customProperties = JdbcUtils.parseJdbcParameters(config, JdbcUtils.JDBC_URL_PARAMS_KEY);
    final Map<String, String> defaultProperties = getDefaultConnectionProperties(config);
    assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties);
    return MoreMaps.merge(customProperties, defaultProperties);
  }

  private void assertCustomParametersDontOverwriteDefaultParameters(final Map<String, String> customParameters,
                                                                    final Map<String, String> defaultParameters) {
    for (final String key : defaultParameters.keySet()) {
      if (customParameters.containsKey(key) && !Objects.equals(customParameters.get(key), defaultParameters.get(key))) {
        throw new IllegalArgumentException("Cannot overwrite default JDBC parameter " + key);
      }
    }
  }

  protected abstract Map<String, String> getDefaultConnectionProperties(final JsonNode config);

  public abstract JsonNode toJdbcConfig(JsonNode config);

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    return JdbcBufferedConsumerFactory.create(outputRecordCollector, getDatabase(getDataSource(config)), sqlOperations, namingResolver, config,
        catalog);
  }

}
