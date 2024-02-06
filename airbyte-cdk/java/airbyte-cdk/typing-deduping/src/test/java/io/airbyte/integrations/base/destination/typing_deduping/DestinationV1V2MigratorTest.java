/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES;
import static org.mockito.ArgumentMatchers.any;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.Optional;
import java.util.stream.Stream;
import lombok.SneakyThrows;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.mockito.Mockito;

public class DestinationV1V2MigratorTest {

  private static final StreamId STREAM_ID = new StreamId("final", "final_table", "raw", "raw_table", null, null);

  public static class ShouldMigrateTestArgumentProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {

      // Don't throw an exception
      final boolean v2SchemaMatches = true;

      return Stream.of(
          // Doesn't Migrate because of sync mode
          Arguments.of(DestinationSyncMode.OVERWRITE, makeMockMigrator(true, false, v2SchemaMatches, true, true), false),
          // Doesn't migrate because v2 table already exists
          Arguments.of(DestinationSyncMode.APPEND, makeMockMigrator(true, true, v2SchemaMatches, true, true), false),
          Arguments.of(DestinationSyncMode.APPEND_DEDUP, makeMockMigrator(true, true, v2SchemaMatches, true, true), false),
          // Doesn't migrate because no valid v1 raw table exists
          Arguments.of(DestinationSyncMode.APPEND, makeMockMigrator(true, false, v2SchemaMatches, false, true), false),
          Arguments.of(DestinationSyncMode.APPEND_DEDUP, makeMockMigrator(true, false, v2SchemaMatches, false, true), false),
          Arguments.of(DestinationSyncMode.APPEND, makeMockMigrator(true, false, v2SchemaMatches, true, false), false),
          Arguments.of(DestinationSyncMode.APPEND_DEDUP, makeMockMigrator(true, false, v2SchemaMatches, true, false), false),
          // Migrates
          Arguments.of(DestinationSyncMode.APPEND, noIssuesMigrator(), true),
          Arguments.of(DestinationSyncMode.APPEND_DEDUP, noIssuesMigrator(), true));
    }

  }

  @ParameterizedTest
  @ArgumentsSource(ShouldMigrateTestArgumentProvider.class)
  public void testShouldMigrate(final DestinationSyncMode destinationSyncMode, final BaseDestinationV1V2Migrator migrator, final boolean expected)
      throws Exception {
    final StreamConfig config = new StreamConfig(STREAM_ID, null, destinationSyncMode, null, null, null);
    final var actual = migrator.shouldMigrate(config);
    Assertions.assertEquals(expected, actual);
  }

  @Test
  public void testMismatchedSchemaThrowsException() throws Exception {
    final StreamConfig config = new StreamConfig(STREAM_ID, null, DestinationSyncMode.APPEND_DEDUP, null, null, null);
    final var migrator = makeMockMigrator(true, true, false, false, false);
    final UnexpectedSchemaException exception = Assertions.assertThrows(UnexpectedSchemaException.class,
        () -> migrator.shouldMigrate(config));
    Assertions.assertEquals("Destination V2 Raw Table does not match expected Schema", exception.getMessage());
  }

  @SneakyThrows
  @Test
  public void testMigrate() throws Exception {
    final var sqlGenerator = new MockSqlGenerator();
    final StreamConfig stream = new StreamConfig(STREAM_ID, null, DestinationSyncMode.APPEND_DEDUP, null, null, null);
    final DestinationHandler<String> handler = Mockito.mock(DestinationHandler.class);
    final var sql = sqlGenerator.migrateFromV1toV2(STREAM_ID, "v1_raw_namespace", "v1_raw_table");
    // All is well
    final var migrator = noIssuesMigrator();
    migrator.migrate(sqlGenerator, handler, stream);
    Mockito.verify(handler).execute(sql);
    // Exception thrown when executing sql, TableNotMigratedException thrown
    Mockito.doThrow(Exception.class).when(handler).execute(any());
    final TableNotMigratedException exception = Assertions.assertThrows(TableNotMigratedException.class,
        () -> migrator.migrate(sqlGenerator, handler, stream));
    Assertions.assertEquals("Attempted and failed to migrate stream final_table", exception.getMessage());
  }

  public static BaseDestinationV1V2Migrator makeMockMigrator(final boolean v2NamespaceExists,
                                                             final boolean v2TableExists,
                                                             final boolean v2RawSchemaMatches,
                                                             final boolean v1RawTableExists,
                                                             final boolean v1RawTableSchemaMatches)
      throws Exception {
    final BaseDestinationV1V2Migrator migrator = Mockito.spy(BaseDestinationV1V2Migrator.class);
    Mockito.when(migrator.doesAirbyteInternalNamespaceExist(any())).thenReturn(v2NamespaceExists);
    final var existingTable = v2TableExists ? Optional.of("v2_raw") : Optional.empty();
    Mockito.when(migrator.getTableIfExists("raw", "raw_table")).thenReturn(existingTable);
    Mockito.when(migrator.schemaMatchesExpectation("v2_raw", V2_RAW_TABLE_COLUMN_NAMES)).thenReturn(v2RawSchemaMatches);

    Mockito.when(migrator.convertToV1RawName(any())).thenReturn(new NamespacedTableName("v1_raw_namespace", "v1_raw_table"));
    final var existingV1RawTable = v1RawTableExists ? Optional.of("v1_raw") : Optional.empty();
    Mockito.when(migrator.getTableIfExists("v1_raw_namespace", "v1_raw_table")).thenReturn(existingV1RawTable);
    Mockito.when(migrator.schemaMatchesExpectation("v1_raw", LEGACY_RAW_TABLE_COLUMNS)).thenReturn(v1RawTableSchemaMatches);
    return migrator;
  }

  public static BaseDestinationV1V2Migrator noIssuesMigrator() throws Exception {
    return makeMockMigrator(true, false, true, true, true);
  }

}
