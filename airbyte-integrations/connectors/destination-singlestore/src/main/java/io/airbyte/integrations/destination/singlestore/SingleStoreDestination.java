/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import static io.airbyte.cdk.db.jdbc.JdbcUtils.DATABASE_KEY;
import static io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage;
import static io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination.RAW_SCHEMA_OVERRIDE;
import static io.airbyte.cdk.integrations.util.ConfiguredCatalogUtilKt.addDefaultNamespaceToStreams;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.*;
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer;
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.integrations.base.destination.operation.DefaultFlush;
import io.airbyte.integrations.base.destination.operation.DefaultSyncOperation;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreDestinationHandler;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreNamingTransformer;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreSqlGenerator;
import io.airbyte.integrations.destination.singlestore.operation.SingleStoreStorageOperations;
import io.airbyte.integrations.destination.singlestore.operation.SingleStoreStreamOperationFactory;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.sql.SQLException;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.function.Consumer;
import org.apache.commons.lang3.concurrent.BasicThreadFactory;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreDestination.class);

  @Override
  public boolean isV2Destination() {
    return true;
  }

  @Nullable
  @Override
  public AirbyteMessageConsumer getConsumer(@NotNull JsonNode jsonNode,
                                            @NotNull ConfiguredAirbyteCatalog configuredAirbyteCatalog,
                                            @NotNull Consumer<AirbyteMessage> consumer) {
    throw new UnsupportedOperationException("GetConsumer is not supported, use getSerializedMessageConsumer");
  }

  @Nullable
  @Override
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(@NotNull JsonNode config,
                                                                       @NotNull ConfiguredAirbyteCatalog catalog,
                                                                       @NotNull Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    var defaultNamespace = config.get(JdbcUtils.DATABASE_KEY).asText();
    addDefaultNamespaceToStreams(catalog, defaultNamespace);
    var rawSchemaOverride = config.has(RAW_SCHEMA_OVERRIDE) ? config.get(RAW_SCHEMA_OVERRIDE).asText() : defaultNamespace;
    var sqlGenerator = new SingleStoreSqlGenerator(new SingleStoreNamingTransformer());
    var catalogParser = new CatalogParser(sqlGenerator, rawSchemaOverride);
    var parsedCatalog = catalogParser.parseCatalog(catalog);
    var datasource = SingleStoreConnectorFactory.createDataSource(config);
    var jdbcDatabase = new DefaultJdbcDatabase(datasource);
    var destinationHandler = new SingleStoreDestinationHandler(jdbcDatabase);
    var storageOperations = new SingleStoreStorageOperations(sqlGenerator, destinationHandler);
    var syncOperations =
        new DefaultSyncOperation<>(
            parsedCatalog,
            destinationHandler,
            config.get(DATABASE_KEY).asText(),
            new SingleStoreStreamOperationFactory(storageOperations),
            new ArrayList<>(),
            false,
            Executors.newFixedThreadPool(
                10,
                new BasicThreadFactory.Builder().namingPattern("sync-operations-%d").build()));
    return new AsyncStreamConsumer(
        outputRecordCollector,
        () -> {},
        (e, streamDescriptorStreamSyncSummaryMap) -> syncOperations.finalizeStreams(streamDescriptorStreamSyncSummaryMap),
        new DefaultFlush(128 * 1024L * 1024L, syncOperations),
        catalog,
        new BufferManager((long) (Runtime.getRuntime().maxMemory() * BufferManager.MEMORY_LIMIT_RATIO)),
        Optional.of(defaultNamespace));
  }

  @Override
  public AirbyteConnectionStatus check(@NotNull JsonNode config) {
    var datasource = SingleStoreConnectorFactory.createDataSource(config);
    try {
      var defaultNamespace = config.get(JdbcUtils.DATABASE_KEY).asText();
      var database = new DefaultJdbcDatabase(datasource);
      var namingResolver = new SingleStoreNamingTransformer();
      var handler = new SingleStoreDestinationHandler(database);
      var sqlGenerator = new SingleStoreSqlGenerator(namingResolver);
      final String outputDatabase = namingResolver.getIdentifier(defaultNamespace);
      var outputTableName =
          namingResolver.getIdentifier("_airbyte_connection_test_" + UUID.randomUUID().toString().replace("-", ""));
      handler.execute(sqlGenerator.createSchema(outputDatabase));
      var streamId = new StreamId("test_final", "test_final", outputDatabase, outputTableName, outputDatabase, outputTableName);
      handler.execute(sqlGenerator.createRawTable(streamId));
      try {
        var insertStmt = MessageFormat.format("INSERT INTO {0}.{1} VALUES(''{2}'', {3}, {3}, ''{4}'', ''{4}'', {5})",
            outputDatabase, outputTableName, UUID.randomUUID().toString(), "NOW(6)", "{ \"field1\": true }", 1);
        handler.execute(Sql.of(insertStmt));
      } finally {
        handler.execute(Sql.of(String.format("DROP TABLE IF EXISTS %s.%s", outputDatabase, outputTableName)));
      }
      handler.verifyLocalFileEnabled();
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final ConnectionErrorException e) {
      final String message = getErrorMessage(e.getStateCode(), e.getErrorCode(), e.getExceptionMessage(), e);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage(message);
    } catch (SQLException e) {
      if (Objects.isNull(e.getCause()) || !(e.getCause() instanceof SQLException)) {
        throw new ConnectionErrorException(e.getSQLState(), e.getErrorCode(), e.getMessage(), e);
      } else {
        var cause = (SQLException) e.getCause();
        throw new ConnectionErrorException(cause.getSQLState(), cause.getErrorCode(), cause.getMessage(), cause);
      }
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(datasource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new SingleStoreDestination();
    LOGGER.info("starting destination: {}", SingleStoreDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", SingleStoreDestination.class);
  }

}
