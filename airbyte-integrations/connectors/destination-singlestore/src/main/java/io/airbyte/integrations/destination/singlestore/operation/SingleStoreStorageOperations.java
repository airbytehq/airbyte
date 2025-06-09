/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.operation;

import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.base.destination.operation.StorageOperation;
import io.airbyte.integrations.base.destination.typing_deduping.*;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreSqlGenerator;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreStorageOperations implements StorageOperation<SerializableBuffer> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreStorageOperations.class);
  private final SingleStoreSqlGenerator sqlGenerator;
  private final DestinationHandler<MinimumDestinationState.Impl> destinationHandler;

  public SingleStoreStorageOperations(SingleStoreSqlGenerator sqlGenerator, DestinationHandler<MinimumDestinationState.Impl> destinationHandler) {
    this.sqlGenerator = sqlGenerator;
    this.destinationHandler = destinationHandler;
  }

  @Override
  public void cleanupStage(@NotNull StreamId streamId) {

  }

  @Override
  public void prepareStage(@NotNull StreamId streamId, @NotNull DestinationSyncMode destinationSyncMode) {
    try {
      var rawDatabase = streamId.getRawNamespace();
      destinationHandler.execute(sqlGenerator.createSchema(rawDatabase));
      destinationHandler.execute(sqlGenerator.createRawTable(streamId));
      // Truncate the raw table if sync in OVERWRITE.
      if (destinationSyncMode == DestinationSyncMode.OVERWRITE) {
        destinationHandler.execute(sqlGenerator.truncateRawTable(streamId));
      }
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void writeToStage(@NotNull StreamConfig streamConfig, SerializableBuffer serializableBuffer) {
    try {
      final String absoluteFile = "'" + Objects.requireNonNull(serializableBuffer.getFile()).getAbsolutePath() + "'";
      final String query = String.format("LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s FIELDS TERMINATED BY " +
          "',' ENCLOSED BY '\"' LINES TERMINATED BY '\\r\\n' NULL DEFINED BY ''", absoluteFile,
          streamConfig.getId().getRawNamespace(), streamConfig.getId().getRawName());
      destinationHandler.execute(Sql.of(query));
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void createFinalTable(@NotNull StreamConfig streamConfig, @NotNull String suffix, boolean replace) {
    try {
      destinationHandler.execute(sqlGenerator.createTable(streamConfig, suffix, replace));
    } catch (Exception e) {
      LOGGER.error("Failed to create final table", e);
      throw new RuntimeException(e);
    }
  }

  @Override
  public void softResetFinalTable(@NotNull StreamConfig streamConfig) {
    try {
      TyperDeduperUtil.executeSoftReset(
          sqlGenerator,
          destinationHandler,
          streamConfig);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void overwriteFinalTable(@NotNull StreamConfig streamConfig, @NotNull String tmpTableSuffix) {
    try {
      destinationHandler.execute(
          sqlGenerator.overwriteFinalTable(streamConfig.getId(), tmpTableSuffix));
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void typeAndDedupe(@NotNull StreamConfig streamConfig, @NotNull Optional<Instant> maxProcessedTimestamp, @NotNull String finalTableSuffix) {
    try {
      TyperDeduperUtil.executeTypeAndDedupe(
          sqlGenerator,
          destinationHandler,
          streamConfig,
          maxProcessedTimestamp,
          finalTableSuffix);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

}
