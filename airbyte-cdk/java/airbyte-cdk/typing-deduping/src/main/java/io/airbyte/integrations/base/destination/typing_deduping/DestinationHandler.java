/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.time.Instant;
import java.util.Optional;

public interface DestinationHandler<DialectTableDefinition> {

  Optional<DialectTableDefinition> findExistingTable(StreamId id) throws Exception;

  boolean isFinalTableEmpty(StreamId id) throws Exception;

  /**
   * Returns the highest timestamp such that all records with _airbyte_extracted equal to or earlier
   * than that timestamp have non-null _airbyte_loaded_at.
   * <p>
   * If the raw table is empty or does not exist, return an empty optional.
   */
  InitialRawTableState getInitialRawTableState(StreamId id) throws Exception;

  record InitialRawTableState(boolean hasUnprocessedRecords, Optional<Instant> maxProcessedTimestamp) {}

  void execute(final String sql) throws Exception;

}
