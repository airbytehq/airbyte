package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Optional;

public record DestinationInitialStateImpl<TableDefinition>(StreamConfig streamConfig,
                                                           Optional<TableDefinition> finalTableDefinition,
                                                           InitialRawTableState initialRawTableState,
                                                           boolean isSchemaMismatch,
                                                           boolean isFinalTableEmpty) implements DestinationInitialState<TableDefinition> {

}
