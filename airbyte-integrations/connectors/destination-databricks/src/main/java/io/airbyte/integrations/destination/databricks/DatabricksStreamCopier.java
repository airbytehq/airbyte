/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This implementation is similar to {@link StreamCopier}. It does the following operations:
 * <ul>
 * <li>1. Writes data stream into staging file(s) in cloud storage.</li>
 * <li>2. Create a tmp delta table based on the staging file(s).</li>
 * <li>3. Create the destination delta table based on the tmp delta table schema.</li>
 * <li>4. Copy the staging file(s) into the destination delta table.</li>
 * <li>5. Delete the tmp delta table, and the staging file(s).</li>
 * </ul>
 */
public abstract class DatabricksStreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksStreamCopier.class);

  protected final String schemaName;
  protected final String streamName;
  protected final DestinationSyncMode destinationSyncMode;
  private final boolean purgeStagingData;
  protected final JdbcDatabase database;
  protected final DatabricksSqlOperations sqlOperations;

  protected final String tmpTableName;
  protected final String destTableName;
  protected final String stagingFolder;
  protected final StagingFilenameGenerator filenameGenerator;
  protected final ConfiguredAirbyteStream configuredStream;
  protected final DatabricksDestinationConfig databricksConfig;

  public DatabricksStreamCopier(final String stagingFolder,
                                final String schema,
                                final ConfiguredAirbyteStream configuredStream,
                                final JdbcDatabase database,
                                final DatabricksDestinationConfig databricksConfig,
                                final ExtendedNameTransformer nameTransformer,
                                final SqlOperations sqlOperations) {
    this.schemaName = schema;
    this.streamName = configuredStream.getStream().getName();
    this.destinationSyncMode = configuredStream.getDestinationSyncMode();
    this.purgeStagingData = databricksConfig.isPurgeStagingData();
    this.database = database;
    this.sqlOperations = (DatabricksSqlOperations) sqlOperations;

    this.databricksConfig = databricksConfig;

    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.destTableName = nameTransformer.getIdentifier(streamName);
    this.stagingFolder = stagingFolder;

    this.filenameGenerator = new StagingFilenameGenerator(streamName, GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES);
    this.configuredStream = configuredStream;

    LOGGER.info("[Stream {}] Database schema: {}", streamName, schemaName);
  }

  protected abstract String getTmpTableLocation();

  protected abstract String getDestTableLocation();

  @Override
  public void createDestinationSchema() throws Exception {
    LOGGER.info("[Stream {}] Creating database schema if it does not exist: {}", streamName, schemaName);
    sqlOperations.createSchemaIfNotExists(database, schemaName);
  }

  @Override
  public void createTemporaryTable() throws Exception {
    LOGGER.info("[Stream {}] Creating tmp table {} from staging file: {}", streamName, tmpTableName, getTmpTableLocation());

    sqlOperations.dropTableIfExists(database, schemaName, tmpTableName);

    final String createTmpTable = getCreateTempTableStatement();

    LOGGER.info(createTmpTable);
    database.execute(createTmpTable);
  }

  protected abstract String getCreateTempTableStatement();

  @Override
  public void copyStagingFileToTemporaryTable() {
    // The tmp table is created directly based on the staging file. So no separate copying step is
    // needed.
  }

  @Override
  public String createDestinationTable() throws Exception {
    LOGGER.info("[Stream {}] Creating destination table if it does not exist: {}", streamName, destTableName);

    final String createStatement = destinationSyncMode == DestinationSyncMode.OVERWRITE
        // "create or replace" is the recommended way to replace existing table
        ? "CREATE OR REPLACE TABLE"
        : "CREATE TABLE IF NOT EXISTS";

    final String createTable = String.format(
        "%s %s.%s " +
            "USING delta " +
            "LOCATION '%s' " +
            "COMMENT 'Created from stream %s' " +
            "TBLPROPERTIES ('airbyte.destinationSyncMode' = '%s', %s) " +
            // create the table based on the schema of the tmp table
            "AS SELECT * FROM %s.%s LIMIT 0",
        createStatement,
        schemaName, destTableName,
        getDestTableLocation(),
        streamName,
        destinationSyncMode.value(),
        String.join(", ", DatabricksConstants.DEFAULT_TBL_PROPERTIES),
        schemaName, tmpTableName);
    LOGGER.info(createTable);
    database.execute(createTable);

    return destTableName;
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    if (purgeStagingData) {
      LOGGER.info("[Stream {}] Deleting tmp table: {}", streamName, tmpTableName);
      sqlOperations.dropTableIfExists(database, schemaName, tmpTableName);

      deleteStagingFile();
    }
  }

  protected abstract void deleteStagingFile();

}
