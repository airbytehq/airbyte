/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.protocol.models.v0.DestinationSyncMode.APPEND;
import static io.airbyte.protocol.models.v0.DestinationSyncMode.OVERWRITE;
import static io.trino.plugin.iceberg.TypeConverter.toTrinoType;
import static io.trino.type.InternalTypeManager.TESTING_TYPE_MANAGER;
import static java.lang.String.format;
import static java.util.Locale.ENGLISH;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This implementation is similar to {@link StreamCopier}. It performs the following operations:
 * <ul>
 * <li>1. Writes data stream into tmp Iceberg table in cloud storage.</li>
 * <li>2. Creates(or modifies the schema of) the destination Iceberg table in Galaxy Catalog based
 * on the tmp Iceberg table schema.</li>
 * <li>4. Copies the tmp Iceberg table into the destination Iceberg table in Galaxy Catalog.</li>
 * <li>5. Deletes the tmp Iceberg table.</li>
 * </ul>
 */
public abstract class StarburstGalaxyStreamCopier
    implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(StarburstGalaxyStreamCopier.class);

  private final String quotedDestTableName;
  private final DestinationSyncMode destinationSyncMode;
  private final boolean purgeStagingTable;
  private final JdbcDatabase database;
  private final StarburstGalaxySqlOperations sqlOperations;

  protected final String schemaName;
  protected final String quotedSchemaName;
  protected final String streamName;
  protected final String tmpTableName;
  protected final String stagingFolder;
  protected final StarburstGalaxyDestinationConfig galaxyDestinationConfig;
  protected TableSchema galaxySchema;

  public StarburstGalaxyStreamCopier(final String stagingFolder,
                                     final String schemaName,
                                     final ConfiguredAirbyteStream configuredStream,
                                     final JdbcDatabase database,
                                     final StarburstGalaxyDestinationConfig galaxyDestinationConfig,
                                     final StandardNameTransformer nameTransformer,
                                     final SqlOperations sqlOperations) {
    this.schemaName = schemaName;
    this.quotedSchemaName = "\"" + this.schemaName + "\""; // Wrap schema name with double quotes to support Galaxy reserved keywords
    this.streamName = configuredStream.getStream().getName();
    this.destinationSyncMode = configuredStream.getDestinationSyncMode();
    this.purgeStagingTable = galaxyDestinationConfig.purgeStagingData();
    this.database = database;
    this.sqlOperations = (StarburstGalaxySqlOperations) sqlOperations;
    this.galaxyDestinationConfig = galaxyDestinationConfig;
    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.quotedDestTableName = "\"" + nameTransformer.getIdentifier(streamName) + "\""; // Wrap table name with double quotes to support Galaxy
                                                                                        // reserved
    // keywords
    this.stagingFolder = stagingFolder;
    LOGGER.info("[Stream {}] Catalog schema: {}", streamName, this.schemaName);
  }

  static TableSchema convertIcebergSchemaToGalaxySchema(org.apache.iceberg.Schema icebergSchema) {
    TableSchema tableSchema = new TableSchema();
    icebergSchema.columns()
        .forEach(
            // Wrap column name in double quotes to support reserved keywords
            column -> tableSchema
                .addColumn(new ColumnMetadata("\"" + column.name() + "\"", toTrinoType(column.type(), TESTING_TYPE_MANAGER), column.fieldId())));
    return tableSchema;
  }

  protected abstract String getTmpTableLocation();

  @Override
  public void createDestinationSchema() throws Exception {
    LOGGER.info("[Stream {}] Create schema if it does not exist: {}", streamName, schemaName);
    sqlOperations.createSchemaIfNotExists(database, quotedSchemaName);
  }

  @Override
  public void createTemporaryTable() throws Exception {
    String registerTable = format("""
                                  CALL system.register_table(schema_name => '%s', table_name => '%s',
                                  table_location => '%s',
                                  metadata_file_name => '%s')
                                  """, schemaName, tmpTableName, getTmpTableLocation(), getTmpTableMetadataFileName());
    LOGGER.info("[Stream {}] Register table: {}", streamName, registerTable);
    database.execute(registerTable);
    LOGGER.info("[Stream {}] Table {} is registered", streamName, tmpTableName);
  }

  protected abstract String getTmpTableMetadataFileName()
      throws IOException, InterruptedException;

  @Override
  public void copyStagingFileToTemporaryTable() {
    // The tmp table is created directly based on the staging file. So no separate copying step is
    // needed.
  }

  /**
   * Adds newly created source columns to target
   */
  private void promoteSourceSchemaChangesToDestination()
      throws SQLException {
    List<JsonNode> describeTable = database.queryJsons(format("DESCRIBE %s.%s", quotedSchemaName, quotedDestTableName));
    LOGGER.info("[Stream {}] Existing table structure for {}.{} table is {}", streamName, schemaName, quotedDestTableName, describeTable);
    Map<String, String> existingColumns = describeTable.stream().collect(
        // Column name is wrapped within double quotes as column name in Galaxy schema is wrapped within
        // double quotes when the schema is created
        Collectors.toMap(column -> "\"" + column.get("Column").asText().toLowerCase(ENGLISH) + "\"",
            column -> column.get("Type").asText().toLowerCase(ENGLISH)));
    galaxySchema.columns().forEach(columnMetadata -> {
      String columnName = columnMetadata.name().toLowerCase(ENGLISH);
      if (!existingColumns.containsKey(columnName)) {
        try {
          String alterTable =
              format(
                  "ALTER TABLE %s.%s ADD COLUMN IF NOT EXISTS %s %s",
                  quotedSchemaName,
                  quotedDestTableName,
                  columnName,
                  columnMetadata.galaxyIcebergType().getDisplayName());
          LOGGER.info("[Stream {}] Add column {} : {}", streamName, columnName, alterTable);
          database.execute(alterTable);
        } catch (SQLException e) {
          throw new RuntimeException(e);
        }
      }
    });
  }

  @Override
  public String createDestinationTable() throws Exception {
    if (destinationSyncMode == OVERWRITE) {
      // Drop existing table to propagate source schema changes
      String dropTable = format("DROP TABLE IF EXISTS %s.%s", quotedSchemaName, quotedDestTableName);
      LOGGER.info("[Stream {}] Dropping destination table: {}", streamName, dropTable);
      database.execute(dropTable);
    }

    String fields = galaxySchema.columns().stream()
        .map(columnMetadata -> format("%s %s",
            columnMetadata.name(),
            columnMetadata.galaxyIcebergType().getDisplayName()))
        .collect(Collectors.joining(", "));
    String createTable =
        format("CREATE TABLE IF NOT EXISTS %s.%s (%s) WITH (format = 'PARQUET', type = 'ICEBERG')", quotedSchemaName, quotedDestTableName, fields);
    LOGGER.info("[Stream {}] Create destination table if it does not exist: {}", streamName, createTable);
    database.execute(createTable);
    if (destinationSyncMode == APPEND) {
      LOGGER.info("[Stream {}] Promote new columns from source to target", streamName);
      promoteSourceSchemaChangesToDestination();
    }

    return quotedDestTableName;
  }

  @Override
  public void removeFileAndDropTmpTable()
      throws SQLException {
    if (purgeStagingTable) {
      LOGGER.info("[Stream {}] Delete tmp table: {}", streamName, tmpTableName);
      sqlOperations.dropTableIfExists(database, quotedSchemaName, tmpTableName);
    }
  }

}
