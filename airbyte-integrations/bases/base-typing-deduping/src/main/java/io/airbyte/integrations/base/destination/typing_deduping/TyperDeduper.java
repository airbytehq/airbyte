package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * An abstraction over SqlGenerator and DestinationHandler. Destinations will still need to
 * call {@code new CatalogParser(new FooSqlGenerator()).parseCatalog()}, but should otherwise
 * avoid interacting directly with these classes.
 * <p>
 * In a typical sync, destinations should call the methods:
 * <ol>
 *   <li>{@link #createFinalTables()} once at the start of the sync</li>
 *   <li>{@link #typeAndDedupe(String, String)} as needed throughoug the sync</li>
 *   <li>{@link #commitFinalTable(String, String)} once at the end of the sync</li>
 * </ol>
 * Note that createFinalTables initializes some internal state. The other methods will throw an exception
 * if that method was not called.
 */
public class TyperDeduper<DialectTableDefinition> {
  private static final Logger LOGGER = LoggerFactory.getLogger(TyperDeduper.class);

  private static final String NO_SUFFIX = "";
  private static final String TMP_OVERWRITE_TABLE_SUFFIX = "_airbyte_tmp";

  private final SqlGenerator<DialectTableDefinition> sqlGenerator;
  private final DestinationHandler<DialectTableDefinition> destinationHandler;
  private final ParsedCatalog parsedCatalog;
  private Map<StreamId, String> overwriteStreamsWithTmpTable;

  public TyperDeduper(SqlGenerator<DialectTableDefinition> sqlGenerator,
                      DestinationHandler<DialectTableDefinition> destinationHandler,
                      ParsedCatalog parsedCatalog) {
    this.sqlGenerator = sqlGenerator;
    this.destinationHandler = destinationHandler;
    this.parsedCatalog = parsedCatalog;
  }

  /**
   * Create the tables that T+D will write to during the sync. In OVERWRITE mode, these might not be the true final tables.
   * Specifically, other than an initial sync (i.e. table does not exist, or is empty) we write to a temporary final table,
   * and swap it into the true final table at the end of the sync. This is to prevent user downtime during a sync.
   */
  public void createFinalTables() throws Exception {
    if (overwriteStreamsWithTmpTable != null) {
      throw new IllegalStateException("createFinalTables() has already been called. This is probably a bug.");
    }
    overwriteStreamsWithTmpTable = new HashMap<>();

    // For each stream, make sure that its corresponding final table exists.
    // Also, for OVERWRITE streams, decide if we're writing directly to the final table, or into an _airbyte_tmp table.
    for (StreamConfig stream : parsedCatalog.streams()) {
      final Optional<DialectTableDefinition> existingTable = destinationHandler.findExistingTable(stream.id());
      if (existingTable.isEmpty()) {
        // If the table doesn't exist, create it
        destinationHandler.execute(sqlGenerator.createTable(stream, NO_SUFFIX));
        if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
          // We're creating this table for the first time. Write directly into it.
          overwriteStreamsWithTmpTable.put(stream.id(), NO_SUFFIX);
        }
      } else {
        // If the table _does_ exist, make sure it has the right schema
        destinationHandler.execute(sqlGenerator.alterTable(stream, existingTable.get()));
        if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
          if (destinationHandler.isFinalTableEmpty(stream.id())) {
            // The table already exists but is empty. We'll load data incrementally.
            // (this might be because the user ran a reset, which creates an empty table)
            overwriteStreamsWithTmpTable.put(stream.id(), NO_SUFFIX);
          } else {
            // We're working with an existing table. Write into a tmp table. We'll overwrite the table at the
            // end of the sync.
            overwriteStreamsWithTmpTable.put(stream.id(), TMP_OVERWRITE_TABLE_SUFFIX);
            destinationHandler.execute(sqlGenerator.createTable(stream, TMP_OVERWRITE_TABLE_SUFFIX));
          }
        }
      }
    }
  }

  /**
   * Execute typing and deduping for a stream (i.e. fetch new raw records into the final table, etc.).
   * <p>
   * This method is thread-safe; multiple threads can call it concurrently.
   */
  public void typeAndDedupe(String originalNamespace, String originalName) throws Exception {
    final var streamConfig = parsedCatalog.getStream(originalNamespace, originalName);
    String suffix;
    suffix = overwriteStreamsWithTmpTable.getOrDefault(streamConfig.id(), NO_SUFFIX);
    final String sql = sqlGenerator.updateTable(suffix, streamConfig);
    destinationHandler.execute(sql);
  }

  /**
   * Does any "end of sync" work for a stream.For most streams, this is a noop.
   * <p>
   * For OVERWRITE streams where we're writing to a temp table, this is where we swap the temp table into the final table.
   */
  public void commitFinalTable(String originalNamespace, String originalName) throws Exception {
    final var streamConfig = parsedCatalog.getStream(originalNamespace, originalName);
    if (DestinationSyncMode.OVERWRITE.equals(streamConfig.destinationSyncMode())) {
      String finalSuffix = overwriteStreamsWithTmpTable.get(streamConfig.id());
      if (finalSuffix != null && !finalSuffix.isEmpty()) {
        final Optional<String> overwriteFinalTable = sqlGenerator.overwriteFinalTable(finalSuffix, streamConfig.id());
        if (overwriteFinalTable.isPresent()) {
          LOGGER.info("Overwriting final table with tmp table for stream {}.{}", originalNamespace, originalName);
          destinationHandler.execute(overwriteFinalTable.get());
        }
      }
    }
  }
}
