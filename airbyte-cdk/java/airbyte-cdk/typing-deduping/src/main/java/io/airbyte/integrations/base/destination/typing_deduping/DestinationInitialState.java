package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Optional;

/**
 * Interface representing the initial state of a destination table.
 *
 * @param <TableDefinition> type of the table definition.
 */
public interface DestinationInitialState<TableDefinition> {

  StreamConfig streamConfig();

  Optional<TableDefinition> finalTableDefinition();

  InitialRawTableState initialRawTableState();

  boolean isSchemaMismatch();

  boolean isFinalTableEmpty();

}
