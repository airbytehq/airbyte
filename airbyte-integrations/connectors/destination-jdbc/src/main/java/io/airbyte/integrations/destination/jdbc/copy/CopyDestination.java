/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy;

import static io.airbyte.integrations.base.errors.messages.ErrorMessage.getErrorMessage;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class CopyDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(CopyDestination.class);

  /**
   * The default database schema field in the destination config is "schema". To change it, pass the
   * field name to the constructor.
   */
  private String schemaFieldName = "schema";

  public CopyDestination() {}

  public CopyDestination(final String schemaFieldName) {
    this.schemaFieldName = schemaFieldName;
  }

  /**
   * A self contained method for writing a file to the persistence for testing. This method should try
   * to clean up after itself by deleting the file it creates.
   */
  public abstract void checkPersistence(JsonNode config) throws Exception;

  public abstract ExtendedNameTransformer getNameTransformer();

  public abstract DataSource getDataSource(JsonNode config);

  public abstract JdbcDatabase getDatabase(DataSource dataSource);

  public abstract SqlOperations getSqlOperations();

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
      final var outputSchema = nameTransformer.convertStreamName(config.get(schemaFieldName).asText());
      performCreateInsertTestOnDestination(outputSchema, database, nameTransformer);

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

  protected void performCreateInsertTestOnDestination(final String outputSchema,
                                                      final JdbcDatabase database,
                                                      final NamingConventionTransformer nameTransformer)
      throws Exception {
    AbstractJdbcDestination.attemptTableOperations(outputSchema, database, nameTransformer, getSqlOperations(), true);
  }

}
