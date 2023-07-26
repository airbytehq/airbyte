/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DefaultTyperDeduperTest {

  private MockSqlGenerator sqlGenerator;
  private DestinationHandler<String> destinationHandler;
  private TyperDeduper typerDeduper;

  @BeforeEach
  void setup() {
    sqlGenerator = spy(new MockSqlGenerator());
    destinationHandler = mock(DestinationHandler.class);
    ParsedCatalog parsedCatalog = new ParsedCatalog(List.of(
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

    typerDeduper = new DefaultTyperDeduper<>(sqlGenerator, destinationHandler, parsedCatalog);
  }

  /**
   * When there are no existing tables, we should create them and write to them directly.
   */
  @Test
  void emptyDestination() throws Exception {
    when(destinationHandler.findExistingTable(any())).thenReturn(Optional.empty());

    typerDeduper.prepareFinalTables();
    verify(destinationHandler).execute("CREATE TABLE overwrite_ns.overwrite_stream");
    verify(destinationHandler).execute("CREATE TABLE append_ns.append_stream");
    verify(destinationHandler).execute("CREATE TABLE dedup_ns.dedup_stream");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream");
    verify(destinationHandler).execute("UPDATE TABLE overwrite_ns.overwrite_stream");
    typerDeduper.typeAndDedupe("append_ns", "append_stream");
    verify(destinationHandler).execute("UPDATE TABLE append_ns.append_stream");
    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream");
    verify(destinationHandler).execute("UPDATE TABLE dedup_ns.dedup_stream");
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

    typerDeduper.prepareFinalTables();
    verify(destinationHandler).execute("SOFT RESET overwrite_ns.overwrite_stream");
    verify(destinationHandler).execute("SOFT RESET append_ns.append_stream");
    verify(destinationHandler).execute("SOFT RESET dedup_ns.dedup_stream");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream");
    verify(destinationHandler).execute("UPDATE TABLE overwrite_ns.overwrite_stream");
    typerDeduper.typeAndDedupe("append_ns", "append_stream");
    verify(destinationHandler).execute("UPDATE TABLE append_ns.append_stream");
    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream");
    verify(destinationHandler).execute("UPDATE TABLE dedup_ns.dedup_stream");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.commitFinalTables();
    verify(destinationHandler, never()).execute(any());
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

    typerDeduper.prepareFinalTables();
    verify(destinationHandler, never()).execute(any());
  }

  /**
   * When there's an existing nonempty table, we should alter it. For the OVERWRITE stream, we also
   * need to write to a tmp table, and overwrite the real table at the end of the sync.
   */
  @Test
  void existingNonemptyTable() throws Exception {
    when(destinationHandler.findExistingTable(any())).thenReturn(Optional.of("foo"));
    when(destinationHandler.isFinalTableEmpty(any())).thenReturn(false);

    typerDeduper.prepareFinalTables();
    // NB: We only create a tmp table for the overwrite stream, and do _not_ soft reset the existing
    // overwrite stream's table.
    verify(destinationHandler).execute("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp");
    verify(destinationHandler).execute("SOFT RESET append_ns.append_stream");
    verify(destinationHandler).execute("SOFT RESET dedup_ns.dedup_stream");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream");
    // NB: no airbyte_tmp suffix on the non-overwrite streams
    verify(destinationHandler).execute("UPDATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp");
    typerDeduper.typeAndDedupe("append_ns", "append_stream");
    verify(destinationHandler).execute("UPDATE TABLE append_ns.append_stream");
    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream");
    verify(destinationHandler).execute("UPDATE TABLE dedup_ns.dedup_stream");
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
    when(destinationHandler.findExistingTable(any())).thenReturn(Optional.of("foo"));
    when(destinationHandler.isFinalTableEmpty(any())).thenReturn(false);
    when(sqlGenerator.existingSchemaMatchesStreamConfig(any(), any())).thenReturn(true);

    typerDeduper.prepareFinalTables();
    // NB: We only create one tmp table here.
    // Also, we need to alter the existing _real_ table, not the tmp table!
    verify(destinationHandler).execute("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp");
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
  }

  @Test
  void nonexistentStream() {
    assertThrows(IllegalArgumentException.class,
        () -> typerDeduper.typeAndDedupe("nonexistent_ns", "nonexistent_stream"));
    verifyNoInteractions(ignoreStubs(destinationHandler));
  }

}
