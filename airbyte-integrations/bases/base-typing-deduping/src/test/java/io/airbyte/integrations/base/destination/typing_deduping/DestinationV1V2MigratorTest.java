package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
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

  public static class ShouldMigrateTestArgumentProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(ExtensionContext context) throws Exception {
      return Stream.of(
          // Should not migrate
          Arguments.of(MockDestinationV1V2Migrator.shouldMigrateBuilder(true, true, true), false),
          Arguments.of(MockDestinationV1V2Migrator.shouldMigrateBuilder(false, false, false), false),
          Arguments.of(MockDestinationV1V2Migrator.shouldMigrateBuilder(false, true, false), false),
          Arguments.of(MockDestinationV1V2Migrator.shouldMigrateBuilder(false, false, true), false),
          Arguments.of(MockDestinationV1V2Migrator.shouldMigrateBuilder(false, true, true), false),
          Arguments.of(MockDestinationV1V2Migrator.shouldMigrateBuilder(true, false, false), false),
          Arguments.of(MockDestinationV1V2Migrator.shouldMigrateBuilder(true, true, false), false),
          // Should migrate
          Arguments.of(MockDestinationV1V2Migrator.shouldMigrateBuilder(true, false, true), true)
      );
    }
  }

  @ParameterizedTest
  @ArgumentsSource(ShouldMigrateTestArgumentProvider.class)
  public void testShouldMigrate(DestinationV1V2Migrator migrator, boolean expected) {
    StreamConfig config = new StreamConfig(null, null, null, null, null, null);
    final var actual = migrator.shouldMigrate(config);
    Assertions.assertEquals(expected, actual);
  }

  public static class MigrationRequiredForSyncModeTestArgumentProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(ExtensionContext context) {
      return Stream.of(
          Arguments.of(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, false),
          Arguments.of(SyncMode.FULL_REFRESH, DestinationSyncMode.APPEND, true),
          Arguments.of(SyncMode.FULL_REFRESH, DestinationSyncMode.APPEND_DEDUP, true),
          Arguments.of(SyncMode.INCREMENTAL, DestinationSyncMode.OVERWRITE, true),
          Arguments.of(SyncMode.INCREMENTAL, DestinationSyncMode.APPEND, true),
          Arguments.of(SyncMode.INCREMENTAL, DestinationSyncMode.APPEND_DEDUP, true)
      );
    }
  }

  @ParameterizedTest
  @ArgumentsSource(MigrationRequiredForSyncModeTestArgumentProvider.class)
  public void testMigrationRequiredForSyncMode(final SyncMode syncMode, final DestinationSyncMode destinationSyncMode, final boolean expected) {
    final var migrator = new MockDestinationV1V2Migrator();
    final var actual = migrator.isMigrationRequiredForSyncMode(syncMode, destinationSyncMode);
    Assertions.assertEquals(expected, actual);
  }

  @Test
  public void testMismatchedSchemaThrowsException() {
    final var migrator = new MockDestinationV1V2Migrator();
    migrator.setSchemaMatchesExpectationValue(false);
    UnexpectedSchemaException exception = Assertions.assertThrows(UnexpectedSchemaException.class,
        () -> migrator.doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema("foo"));
    Assertions.assertEquals("Destination V2 Raw Table does not match expected Schema", exception.getMessage());
  }

  @Test
  public void testMigrateIfNecessary() {
    final var migrator = new MockDestinationV1V2Migrator();
    // Should Migrate
    migrator.setShouldMigrateValue(true);
    migrator.setMigrationResultValue(new MigrationResult(true));
    final var stream = new StreamConfig(new StreamId("foo", "bar", null, null, null, null), null, null, null, null, null);
    var actual = migrator.migrateIfNecessary(null, null, stream);
    Assertions.assertTrue(actual.isPresent());
    Assertions.assertTrue(actual.get().success());
    // Should not migrate
    migrator.setShouldMigrateValue(false);
    actual = migrator.migrateIfNecessary(null, null, null);
    Assertions.assertFalse(actual.isPresent());
  }

  @SneakyThrows
  @Test
  public void testMigrate() {
    final var sqlGenerator = new MockSqlGenerator();
    final StreamId streamId = new StreamId("foo", "bar", "fizz", "buzz", null, null);
    final StreamConfig stream = new StreamConfig(streamId, null, null, null, null, null);
    final DestinationHandler<String> handler = Mockito.mock(DestinationHandler.class);
    final var migrator = new MockDestinationV1V2Migrator();
    final var v1RawName = new AirbyteStreamNameNamespacePair("zip", "zop");
    migrator.setConvertToV1RawNameValue(v1RawName);
    final var sql = String.join("\n", sqlGenerator.migrateFromV1toV2(stream, v1RawName), sqlGenerator.softReset(stream));
    // All is well
    var actual = migrator.migrate(sqlGenerator, handler, stream);
    Mockito.verify(handler).execute(sql);
    Assertions.assertTrue(actual.success());
    // Exception during SQL Execution
    Mockito.doThrow(Exception.class).when(handler).execute(Mockito.anyString());
    TableNotMigratedException exception = Assertions.assertThrows(TableNotMigratedException.class,
        () -> migrator.migrate(sqlGenerator, handler, stream));
    Assertions.assertEquals("Attempted and failed to migrate stream bar", exception.getMessage());
  }

}
