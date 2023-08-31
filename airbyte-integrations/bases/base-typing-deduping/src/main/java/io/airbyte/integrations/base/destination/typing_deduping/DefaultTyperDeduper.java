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
 * <li>{@link #prepareTables()} once at the start of the sync</li>
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

  private final DestinationV1V2Migrator<DialectTableDefinition> v1V2Migrator;
  private final V2RawTableMigrator<DialectTableDefinition> v2RawTableMigrator;
  private final ParsedCatalog parsedCatalog;
  private Set<StreamId> overwriteStreamsWithTmpTable;
  private final Set<StreamId> streamsWithSuccesfulSetup;

  public DefaultTyperDeduper(final SqlGenerator<DialectTableDefinition> sqlGenerator,
                             final DestinationHandler<DialectTableDefinition> destinationHandler,
                             final ParsedCatalog parsedCatalog,
                             final DestinationV1V2Migrator<DialectTableDefinition> v1V2Migrator,
                             final V2RawTableMigrator<DialectTableDefinition> v2RawTableMigrator) {
    this.sqlGenerator = sqlGenerator;
    this.destinationHandler = destinationHandler;
    this.parsedCatalog = parsedCatalog;
    this.v1V2Migrator = v1V2Migrator;
    this.v2RawTableMigrator = v2RawTableMigrator;
    this.streamsWithSuccesfulSetup = new HashSet<>();
  }

  public DefaultTyperDeduper(
                             final SqlGenerator<DialectTableDefinition> sqlGenerator,
                             final DestinationHandler<DialectTableDefinition> destinationHandler,
                             final ParsedCatalog parsedCatalog,
                             final DestinationV1V2Migrator<DialectTableDefinition> v1V2Migrator) {
    this(sqlGenerator, destinationHandler, parsedCatalog, v1V2Migrator, new NoopV2RawTableMigrator<>());
  }

  /**
   * Create the tables that T+D will write to during the sync. In OVERWRITE mode, these might not be
   * the true final tables. Specifically, other than an initial sync (i.e. table does not exist, or is
   * empty) we write to a temporary final table, and swap it into the true final table at the end of
   * the sync. This is to prevent user downtime during a sync.
   */
  public void prepareTables() throws Exception {
    if (overwriteStreamsWithTmpTable != null) {
      throw new IllegalStateException("Tables were already prepared.");
    }
    overwriteStreamsWithTmpTable = new HashSet<>();
    LOGGER.info("Preparing final tables");

    // For each stream, make sure that its corresponding final table exists.
    // Also, for OVERWRITE streams, decide if we're writing directly to the final table, or into an
    // _airbyte_tmp table.
    for (final StreamConfig stream : parsedCatalog.streams()) {
      // Migrate the Raw Tables if this is the first v2 sync after a v1 sync
      v1V2Migrator.migrateIfNecessary(sqlGenerator, destinationHandler, stream);
      v2RawTableMigrator.migrateIfNecessary(stream);

      final Optional<DialectTableDefinition> existingTable = destinationHandler.findExistingTable(stream.id());
      if (existingTable.isPresent()) {
        LOGGER.info("Final Table exists for stream {}", stream.id().finalName());
        // The table already exists. Decide whether we're writing to it directly, or using a tmp table.
        if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
          if (!destinationHandler.isFinalTableEmpty(stream.id()) || !sqlGenerator.existingSchemaMatchesStreamConfig(stream, existingTable.get())) {
            // We want to overwrite an existing table. Write into a tmp table. We'll overwrite the table at the
            // end of the sync.
            overwriteStreamsWithTmpTable.add(stream.id());
            // overwrite an existing tmp table if needed.
            destinationHandler.execute(sqlGenerator.createTable(stream, TMP_OVERWRITE_TABLE_SUFFIX, true));
            LOGGER.info("Using temp final table for stream {}, will overwrite existing table at end of sync", stream.id().finalName());
          } else {
            LOGGER.info("Final Table for stream {} is empty and matches the expected v2 format, writing to table directly", stream.id().finalName());
          }

        } else if (!sqlGenerator.existingSchemaMatchesStreamConfig(stream, existingTable.get())) {
          // We're loading data directly into the existing table. Make sure it has the right schema.
          LOGGER.info("Existing schema for stream {} is different from expected schema. Executing soft reset.", stream.id().finalTableId(""));
          destinationHandler.execute(sqlGenerator.softReset(stream));
        }
      } else {
        LOGGER.info("Final Table does not exist for stream {}, creating.", stream.id().finalName());
        // The table doesn't exist. Create it. Don't force.
        destinationHandler.execute(sqlGenerator.createTable(stream, NO_SUFFIX, false));
      }

      streamsWithSuccesfulSetup.add(stream.id());
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
  public void typeAndDedupe(final String originalNamespace, final String originalName) throws Exception {
    LOGGER.info("Attempting typing and deduping for {}.{}", originalNamespace, originalName);
    final var streamConfig = parsedCatalog.getStream(originalNamespace, originalName);
    if (streamsWithSuccesfulSetup.stream()
        .noneMatch(streamId -> streamId.originalNamespace().equals(originalNamespace) && streamId.originalName().equals(originalName))) {
      // For example, if T+D setup fails, but the consumer tries to run T+D on all streams during close,
      // we should skip it.
      LOGGER.warn("Skipping typing and deduping for {}.{} because we could not set up the tables for this stream.", originalNamespace, originalName);
      return;
    }
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
    for (final StreamConfig streamConfig : parsedCatalog.streams()) {
      if (!streamsWithSuccesfulSetup.contains(streamConfig.id())) {
        LOGGER.warn("Skipping committing final table for for {}.{} because we could not set up the tables for this stream.",
            streamConfig.id().originalNamespace(), streamConfig.id().originalName());
        continue;
      }
      if (DestinationSyncMode.OVERWRITE.equals(streamConfig.destinationSyncMode())) {
        final StreamId streamId = streamConfig.id();
        final String finalSuffix = getFinalTableSuffix(streamId);
        if (!StringUtils.isEmpty(finalSuffix)) {
          final String overwriteFinalTable = sqlGenerator.overwriteFinalTable(streamId, finalSuffix);
          LOGGER.info("Overwriting final table with tmp table for stream {}.{}", streamId.originalNamespace(), streamId.originalName());
          destinationHandler.execute(overwriteFinalTable);
        }
      }
    }
  }

  private String getFinalTableSuffix(final StreamId streamId) {
    return overwriteStreamsWithTmpTable.contains(streamId) ? TMP_OVERWRITE_TABLE_SUFFIX : NO_SUFFIX;
  }

}
