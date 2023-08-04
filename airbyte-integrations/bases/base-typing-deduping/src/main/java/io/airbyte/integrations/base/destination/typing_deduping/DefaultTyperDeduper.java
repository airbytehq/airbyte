/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.HashSet;
import java.util.Optional;
import java.util.Set;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * An abstraction over SqlGenerator and DestinationHandler. Destinations will still need to call
 * {@code new CatalogParser(new FooSqlGenerator()).parseCatalog()}, but should otherwise avoid
 * interacting directly with these classes.
 * <p>
 * In a typical sync, destinations should call the methods:
 * <ol>
 * <li>{@link #prepareFinalTables()} once at the start of the sync</li>
 * <li>{@link #typeAndDedupe(String, String)} as needed throughout the sync</li>
 * <li>{@link #commitFinalTables()} once at the end of the sync</li>
 * </ol>
 * Note that createFinalTables initializes some internal state. The other methods will throw an
 * exception if that method was not called.
 */
public class DefaultTyperDeduper<DialectTableDefinition> implements TyperDeduper {

  private static final Logger LOGGER = LoggerFactory.getLogger(TyperDeduper.class);

  private static final String NO_SUFFIX = "";
  private static final String TMP_OVERWRITE_TABLE_SUFFIX = "_airbyte_tmp";

  private final SqlGenerator<DialectTableDefinition> sqlGenerator;
  private final DestinationHandler<DialectTableDefinition> destinationHandler;
  private final ParsedCatalog parsedCatalog;
  private Set<StreamId> overwriteStreamsWithTmpTable;

  public DefaultTyperDeduper(SqlGenerator<DialectTableDefinition> sqlGenerator,
                             DestinationHandler<DialectTableDefinition> destinationHandler,
                             ParsedCatalog parsedCatalog) {
    this.sqlGenerator = sqlGenerator;
    this.destinationHandler = destinationHandler;
    this.parsedCatalog = parsedCatalog;
  }

  /**
   * Create the tables that T+D will write to during the sync. In OVERWRITE mode, these might not be
   * the true final tables. Specifically, other than an initial sync (i.e. table does not exist, or is
   * empty) we write to a temporary final table, and swap it into the true final table at the end of
   * the sync. This is to prevent user downtime during a sync.
   */
  public void prepareFinalTables() throws Exception {
    if (overwriteStreamsWithTmpTable != null) {
      throw new IllegalStateException("Tables were already prepared.");
    }
    overwriteStreamsWithTmpTable = new HashSet<>();
    LOGGER.info("Preparing final tables");

    // For each stream, make sure that its corresponding final table exists.
    // Also, for OVERWRITE streams, decide if we're writing directly to the final table, or into an
    // _airbyte_tmp table.
    for (StreamConfig stream : parsedCatalog.streams()) {
      final Optional<DialectTableDefinition> existingTable = destinationHandler.findExistingTable(stream.id());
      if (existingTable.isPresent()) {
        // The table already exists. Decide whether we're writing to it directly, or using a tmp table.
        if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE && !destinationHandler.isFinalTableEmpty(stream.id())) {
          // We want to overwrite an existing table. Write into a tmp table. We'll overwrite the table at the
          // end of the sync.
          overwriteStreamsWithTmpTable.add(stream.id());
          destinationHandler.execute(sqlGenerator.createTable(stream, TMP_OVERWRITE_TABLE_SUFFIX));
        } else if (!sqlGenerator.existingSchemaMatchesStreamConfig(stream, existingTable.get())) {
          // We're loading data directly into the existing table. Make sure it has the right schema.
          LOGGER.info("Existing schema for stream {} is different from expected schema. Executing soft reset.", stream.id().finalTableId(""));
          destinationHandler.execute(sqlGenerator.softReset(stream));
        }
      } else {
        // The table doesn't exist. Create it.
        destinationHandler.execute(sqlGenerator.createTable(stream, NO_SUFFIX));
      }
    }
  }

  /**
   * Execute typing and deduping for a single stream (i.e. fetch new raw records into the final table,
   * etc.).
   * <p>
   * This method is thread-safe; multiple threads can call it concurrently.
   *
   * @param originalNamespace The stream's namespace, as declared in the configured catalog
   * @param originalName The stream's name, as declared in the configured catalog
   */
  public void typeAndDedupe(String originalNamespace, String originalName) throws Exception {
    LOGGER.info("Attempting typing and deduping for {}.{}", originalNamespace, originalName);
    final var streamConfig = parsedCatalog.getStream(originalNamespace, originalName);
    final String suffix = getFinalTableSuffix(streamConfig.id());
    final String sql = sqlGenerator.updateTable(streamConfig, suffix);
    destinationHandler.execute(sql);
  }

  /**
   * Does any "end of sync" work. For most streams, this is a noop.
   * <p>
   * For OVERWRITE streams where we're writing to a temp table, this is where we swap the temp table
   * into the final table.
   */
  public void commitFinalTables() throws Exception {
    LOGGER.info("Committing final tables");
    for (StreamConfig streamConfig : parsedCatalog.streams()) {
      if (DestinationSyncMode.OVERWRITE.equals(streamConfig.destinationSyncMode())) {
        StreamId streamId = streamConfig.id();
        String finalSuffix = getFinalTableSuffix(streamId);
        if (!StringUtils.isEmpty(finalSuffix)) {
          final String overwriteFinalTable = sqlGenerator.overwriteFinalTable(streamId, finalSuffix);
          LOGGER.info("Overwriting final table with tmp table for stream {}.{}", streamId.originalNamespace(), streamId.originalName());
          destinationHandler.execute(overwriteFinalTable);
        }
      }
    }
  }

  private String getFinalTableSuffix(StreamId streamId) {
    return overwriteStreamsWithTmpTable.contains(streamId) ? TMP_OVERWRITE_TABLE_SUFFIX : NO_SUFFIX;
  }

}
