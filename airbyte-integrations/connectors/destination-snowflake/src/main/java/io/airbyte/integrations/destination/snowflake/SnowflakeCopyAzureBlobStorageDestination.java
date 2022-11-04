/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.base.errors.messages.ErrorMessage.getErrorMessage;
import static io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig.getAzureBlobConfig;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageStreamCopier;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeCopyAzureBlobStorageDestination extends CopyDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeCopyAzureBlobStorageDestination.class);

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final DataSource dataSource = getDataSource(config);
    return CopyConsumerFactory.create(
        outputRecordCollector,
        dataSource,
        getDatabase(dataSource),
        getSqlOperations(),
        getNameTransformer(),
        getAzureBlobConfig(config.get("loading_method")),
        catalog,
        new SnowflakeAzureBlobStorageStreamCopierFactory(),
        getConfiguredSchema(config));
  }

  @Override
  public void checkPersistence(final JsonNode config) {
    AzureBlobStorageStreamCopier.attemptAzureBlobWriteAndDelete(getAzureBlobConfig(config.get("loading_method")));
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new SnowflakeSQLNameTransformer();
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    return SnowflakeDatabase.createDataSource(config);
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return SnowflakeDatabase.getDatabase(dataSource);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new SnowflakeSqlOperations();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      checkPersistence(config);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the staging persistence: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the staging persistence with the provided configuration. \n" + e.getMessage());
    }

    final DataSource dataSource = getDataSource(config);

    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final var nameTransformer = getNameTransformer();
      final var outputSchema = nameTransformer.convertStreamName(getConfiguredSchema(config));
      AbstractJdbcDestination.attemptSQLCreateAndDropTableOperations(outputSchema, database, nameTransformer, getSqlOperations(), true);

      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final ConnectionErrorException ex) {
      LOGGER.info("Exception while checking connection: ", ex);
      final String message = getErrorMessage(ex.getStateCode(), ex.getErrorCode(), ex.getExceptionMessage(), ex);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(ex, message);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(message);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to connect to the warehouse: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the warehouse with the provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  private String getConfiguredSchema(final JsonNode config) {
    return config.get("schema").asText();
  }

}
