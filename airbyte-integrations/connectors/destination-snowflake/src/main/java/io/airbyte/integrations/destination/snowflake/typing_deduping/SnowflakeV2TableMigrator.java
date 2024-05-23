/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
import static io.airbyte.integrations.destination.snowflake.SnowflakeDestination.RAW_SCHEMA_OVERRIDE;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil;
import io.airbyte.integrations.base.destination.typing_deduping.V2TableMigrator;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeV2TableMigrator implements V2TableMigrator {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeV2TableMigrator.class);

  private final JdbcDatabase database;
  private final String rawNamespace;
  private final String databaseName;
  private final SnowflakeSqlGenerator generator;
  private final SnowflakeDestinationHandler handler;

  public SnowflakeV2TableMigrator(final JdbcDatabase database,
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
  public void migrateIfNecessary(final StreamConfig streamConfig) throws Exception {
    final StreamId caseSensitiveStreamId = buildStreamId_caseSensitive(
        streamConfig.getId().getOriginalNamespace(),
        streamConfig.getId().getOriginalName(),
        rawNamespace);
    final boolean syncModeRequiresMigration = streamConfig.getDestinationSyncMode() != DestinationSyncMode.OVERWRITE;
    final boolean existingTableCaseSensitiveExists = findExistingTable(caseSensitiveStreamId).isPresent();
    final boolean existingTableUppercaseDoesNotExist = findExistingTable(streamConfig.getId()).isEmpty();
    LOGGER.info(
        "Checking whether upcasing migration is necessary for {}.{}. Sync mode requires migration: {}; existing case-sensitive table exists: {}; existing uppercased table does not exist: {}",
        streamConfig.getId().getOriginalNamespace(),
        streamConfig.getId().getOriginalName(),
        syncModeRequiresMigration,
        existingTableCaseSensitiveExists,
        existingTableUppercaseDoesNotExist);
    if (syncModeRequiresMigration && existingTableCaseSensitiveExists && existingTableUppercaseDoesNotExist) {
      LOGGER.info(
          "Executing upcasing migration for {}.{}",
          streamConfig.getId().getOriginalNamespace(),
          streamConfig.getId().getOriginalName());
      TyperDeduperUtil.executeSoftReset(generator, handler, streamConfig);
    }
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
    if (existingTableMap.containsKey(id.getFinalNamespace()) && existingTableMap.get(id.getFinalNamespace()).containsKey(id.getFinalName())) {
      return Optional.of(existingTableMap.get(id.getFinalNamespace()).get(id.getFinalName()));
    }
    return Optional.empty();
  }

}
