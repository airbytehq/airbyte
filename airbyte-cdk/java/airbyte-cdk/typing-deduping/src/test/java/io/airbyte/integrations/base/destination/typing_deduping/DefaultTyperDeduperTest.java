/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.clearInvocations;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.ignoreStubs;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DefaultTyperDeduperTest {

  private MockSqlGenerator sqlGenerator;
  private DestinationHandler<String> destinationHandler;

  private DestinationV1V2Migrator<String> migrator;
  private TyperDeduper typerDeduper;

  @BeforeEach
  void setup() throws Exception {
    sqlGenerator = spy(new MockSqlGenerator());
    destinationHandler = mock(DestinationHandler.class);
    when(destinationHandler.getMinTimestampForSync(any())).thenReturn(Optional.empty());
    migrator = new NoOpDestinationV1V2Migrator<>();

    final ParsedCatalog parsedCatalog = new ParsedCatalog(List.of(
        new StreamConfig(
            new StreamId("overwrite_ns", "overwrite_stream", null, null, "overwrite_ns", "overwrite_stream"),
            null,
            DestinationSyncMode.OVERWRITE,
            null,
            null,
            null),
        new StreamConfig(
            new StreamId("append_ns", "append_stream", null, null, "append_ns", "append_stream"),
            null,
            DestinationSyncMode.APPEND,
            null,
            null,
            null),
        new StreamConfig(
            new StreamId("dedup_ns", "dedup_stream", null, null, "dedup_ns", "dedup_stream"),
            null,
            DestinationSyncMode.APPEND_DEDUP,
            null,
            null,
            null)));

    typerDeduper = new DefaultTyperDeduper<>(sqlGenerator, destinationHandler, parsedCatalog, migrator, 1);
  }

  /**
   * When there are no existing tables, we should create them and write to them directly.
   */
  @Test
  void emptyDestination() throws Exception {
    when(destinationHandler.findExistingTable(any())).thenReturn(Optional.empty());

    typerDeduper.prepareTables();
    verify(destinationHandler).execute("CREATE TABLE overwrite_ns.overwrite_stream");
    verify(destinationHandler).execute("CREATE TABLE append_ns.append_stream");
    verify(destinationHandler).execute("CREATE TABLE dedup_ns.dedup_stream");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream", false);
    verify(destinationHandler).execute("UPDATE TABLE overwrite_ns.overwrite_stream WITHOUT SAFER CASTING");
    typerDeduper.typeAndDedupe("append_ns", "append_stream", false);
    verify(destinationHandler).execute("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING");
    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream", false);
    verify(destinationHandler).execute("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.commitFinalTables();
    verify(destinationHandler, never()).execute(any());
  }

  /**
   * When there's an existing table but it's empty, we should ensure it has the right schema and write
   * to it directly.
   */
  @Test
  void existingEmptyTable() throws Exception {
    when(destinationHandler.findExistingTable(any())).thenReturn(Optional.of("foo"));
    when(destinationHandler.isFinalTableEmpty(any())).thenReturn(true);
    when(sqlGenerator.existingSchemaMatchesStreamConfig(any(), any())).thenReturn(false);
    typerDeduper.prepareTables();
    verify(destinationHandler).execute("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp");
    verify(destinationHandler).execute("PREPARE append_ns.append_stream FOR SOFT RESET");
    verify(destinationHandler).execute("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING");
    verify(destinationHandler).execute("OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset");
    verify(destinationHandler).execute("PREPARE dedup_ns.dedup_stream FOR SOFT RESET");
    verify(destinationHandler).execute("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING");
    verify(destinationHandler).execute("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream", false);
    verify(destinationHandler).execute("UPDATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp WITHOUT SAFER CASTING");
    typerDeduper.typeAndDedupe("append_ns", "append_stream", false);
    verify(destinationHandler).execute("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING");
    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream", false);
    verify(destinationHandler).execute("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.commitFinalTables();
    verify(destinationHandler).execute("OVERWRITE TABLE overwrite_ns.overwrite_stream FROM overwrite_ns.overwrite_stream_airbyte_tmp");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
  }

  /**
   * When there's an existing empty table with the right schema, we don't need to do anything during
   * setup.
   */
  @Test
  void existingEmptyTableMatchingSchema() throws Exception {
    when(destinationHandler.findExistingTable(any())).thenReturn(Optional.of("foo"));
    when(destinationHandler.isFinalTableEmpty(any())).thenReturn(true);
    when(sqlGenerator.existingSchemaMatchesStreamConfig(any(), any())).thenReturn(true);

    typerDeduper.prepareTables();
    verify(destinationHandler, never()).execute(any());
  }

  /**
   * When there's an existing nonempty table, we should alter it. For the OVERWRITE stream, we also
   * need to write to a tmp table, and overwrite the real table at the end of the sync.
   */
  @Test
  void existingNonemptyTable() throws Exception {
    when(destinationHandler.getMinTimestampForSync(any())).thenReturn(Optional.of(Instant.parse("2023-01-01T12:34:56Z")));
    when(destinationHandler.findExistingTable(any())).thenReturn(Optional.of("foo"));
    when(destinationHandler.isFinalTableEmpty(any())).thenReturn(false);

    typerDeduper.prepareTables();
    // NB: We only create a tmp table for the overwrite stream, and do _not_ soft reset the existing
    // overwrite stream's table.
    verify(destinationHandler).execute("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp");
    verify(destinationHandler).execute("PREPARE append_ns.append_stream FOR SOFT RESET");
    verify(destinationHandler).execute("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING");
    verify(destinationHandler).execute("OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset");
    verify(destinationHandler).execute("PREPARE dedup_ns.dedup_stream FOR SOFT RESET");
    verify(destinationHandler).execute("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING");
    verify(destinationHandler).execute("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream", false);
    // NB: no airbyte_tmp suffix on the non-overwrite streams
    verify(destinationHandler)
        .execute("UPDATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-01T12:34:56Z");
    typerDeduper.typeAndDedupe("append_ns", "append_stream", false);
    verify(destinationHandler).execute("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-01T12:34:56Z");
    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream", false);
    verify(destinationHandler).execute("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-01T12:34:56Z");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.commitFinalTables();
    verify(destinationHandler).execute("OVERWRITE TABLE overwrite_ns.overwrite_stream FROM overwrite_ns.overwrite_stream_airbyte_tmp");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
  }

  /**
   * When there's an existing nonempty table with the right schema, we don't need to modify it, but
   * OVERWRITE streams still need to create a tmp table.
   */
  @Test
  void existingNonemptyTableMatchingSchema() throws Exception {
    when(destinationHandler.getMinTimestampForSync(any())).thenReturn(Optional.of(Instant.now()));
    when(destinationHandler.findExistingTable(any())).thenReturn(Optional.of("foo"));
    when(destinationHandler.isFinalTableEmpty(any())).thenReturn(false);
    when(sqlGenerator.existingSchemaMatchesStreamConfig(any(), any())).thenReturn(true);

    typerDeduper.prepareTables();
    // NB: We only create one tmp table here.
    // Also, we need to alter the existing _real_ table, not the tmp table!
    verify(destinationHandler).execute("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
  }

  @Test
  void nonexistentStream() {
    assertThrows(IllegalArgumentException.class,
        () -> typerDeduper.typeAndDedupe("nonexistent_ns", "nonexistent_stream", false));
    verifyNoInteractions(ignoreStubs(destinationHandler));
  }

  @Test
  void failedSetup() throws Exception {
    doThrow(new RuntimeException("foo")).when(destinationHandler).execute(any());

    assertThrows(Exception.class, () -> typerDeduper.prepareTables());
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream", false);
    typerDeduper.commitFinalTables();

    verifyNoInteractions(ignoreStubs(destinationHandler));
  }

}
