/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Optional;

public interface DestinationHandler<DialectTableDefinition> {

  Optional<DialectTableDefinition> findExistingTable(StreamId id) throws Exception;

  boolean isFinalTableEmpty(StreamId id) throws Exception;

  void execute(final String sql) throws Exception;

}
