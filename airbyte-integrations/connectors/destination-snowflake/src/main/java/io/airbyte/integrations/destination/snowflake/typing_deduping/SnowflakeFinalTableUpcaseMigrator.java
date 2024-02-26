/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
import static io.airbyte.integrations.destination.snowflake.SnowflakeInternalStagingDestination.RAW_SCHEMA_OVERRIDE;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialState;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeTransaction;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.destination.snowflake.typing_deduping.migrations.SnowflakeState;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeFinalTableUpcaseMigrator implements Migration<SnowflakeState> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeFinalTableUpcaseMigrator.class);

  private final JdbcDatabase database;
  private final String rawNamespace;
  private final String databaseName;
  private final SnowflakeSqlGenerator generator;
  private final SnowflakeDestinationHandler handler;

  public SnowflakeFinalTableUpcaseMigrator(final JdbcDatabase database,
                                           final String databaseName,
                                           final SnowflakeSqlGenerator generator,
                                           final SnowflakeDestinationHandler handler) {
    this.database = database;
    this.databaseName = databaseName;
    this.generator = generator;
    this.handler = handler;
    this.rawNamespace = TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).orElse(DEFAULT_AIRBYTE_INTERNAL_NAMESPACE);
  }

  @Override
  public boolean requireMigration(@NotNull SnowflakeState state) {
    return !state.getFinalTableNameUppercase();
  }

  @NotNull
  @Override
  public MigrationResult<SnowflakeState> migrateIfNecessary(
                                                            @NotNull DestinationHandler<SnowflakeState> destinationHandler,
                                                            @NotNull StreamConfig streamConfig,
                                                            @NotNull DestinationInitialState<SnowflakeState> state) {
    final StreamId caseSensitiveStreamId = buildStreamId_caseSensitive(
        streamConfig.id().originalNamespace(),
        streamConfig.id().originalName(),
        rawNamespace);
    final boolean syncModeRequiresMigration = streamConfig.destinationSyncMode() != DestinationSyncMode.OVERWRITE;
    final boolean existingTableCaseSensitiveExists;
    try {
      // Keep this metadata call here. We _could_ shove it into DestinationInitialState,
      // but that's a lot of work for no real gain.
      existingTableCaseSensitiveExists = findExistingTable(caseSensitiveStreamId).isPresent();
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
    final boolean existingTableUppercaseDoesNotExist = state.isFinalTablePresent();
    LOGGER.info(
        "Checking whether upcasing migration is necessary for {}.{}. Sync mode requires migration: {}; existing case-sensitive table exists: {}; existing uppercased table does not exist: {}",
        streamConfig.id().originalNamespace(),
        streamConfig.id().originalName(),
        syncModeRequiresMigration,
        existingTableCaseSensitiveExists,
        existingTableUppercaseDoesNotExist);
    if (syncModeRequiresMigration && existingTableCaseSensitiveExists && existingTableUppercaseDoesNotExist) {
      LOGGER.info(
          "Executing upcasing migration for {}.{}",
          streamConfig.id().originalNamespace(),
          streamConfig.id().originalName());
      // Migrations generally shouldn't actually run a soft reset.
      // However, we actually _need_ to do this here, so that the final table exists correctly.
      // This is so that we can then regather initial state properly.
      try {
        TypeAndDedupeTransaction.executeSoftReset(generator, handler, streamConfig);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
      // TODO switch this file to kotlin + use the copy() method
      final SnowflakeState updatedState = new SnowflakeState(
          // We don't need to trigger a soft reset here, because we've already done it.
          false,
          state.destinationState().getV1V2MigrationDone(),
          // Update the migration status to completed
          true,
          state.destinationState().getExtractedAtInUtc());
      // Invalidate the initial state - SnowflakeDestinationHandler will now be able to find the final
      // tables
      // so we need to refetch it.
      return new MigrationResult<>(updatedState, true);
    }
    return new MigrationResult<>(state.destinationState(), true);
  }

  // These methods were copied from
  // https://github.com/airbytehq/airbyte/blob/d5fdb1b982d464f54941bf9a830b9684fb47d249/airbyte-integrations/connectors/destination-snowflake/src/main/java/io/airbyte/integrations/destination/snowflake/typing_deduping/SnowflakeSqlGenerator.java
  // which is the highest version of destination-snowflake that still uses quoted+case-sensitive
  // identifiers
  private static StreamId buildStreamId_caseSensitive(final String namespace, final String name, final String rawNamespaceOverride) {
    // No escaping needed, as far as I can tell. We quote all our identifier names.
    return new StreamId(
        escapeIdentifier_caseSensitive(namespace),
        escapeIdentifier_caseSensitive(name),
        escapeIdentifier_caseSensitive(rawNamespaceOverride),
        escapeIdentifier_caseSensitive(StreamId.concatenateRawTableName(namespace, name)),
        namespace,
        name);
  }

  private static String escapeIdentifier_caseSensitive(final String identifier) {
    // Note that we don't need to escape backslashes here!
    // The only special character in an identifier is the double-quote, which needs to be doubled.
    return identifier.replace("\"", "\"\"");
  }

  private Optional<TableDefinition> findExistingTable(final StreamId id) throws SQLException {
    // The obvious database.getMetaData().getColumns() solution doesn't work, because JDBC translates
    // VARIANT as VARCHAR
    LinkedHashMap<String, LinkedHashMap<String, TableDefinition>> existingTableMap =
        SnowflakeDestinationHandler.findExistingTables(database, databaseName, List.of(id));
    if (existingTableMap.containsKey(id.finalNamespace()) && existingTableMap.get(id.finalNamespace()).containsKey(id.finalName())) {
      return Optional.of(existingTableMap.get(id.finalNamespace()).get(id.finalName()));
    }
    return Optional.empty();
  }

}
