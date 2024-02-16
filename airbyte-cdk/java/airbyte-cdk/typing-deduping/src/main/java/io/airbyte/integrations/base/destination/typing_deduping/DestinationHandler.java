/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.List;
import java.util.concurrent.CompletableFuture;

public interface DestinationHandler<TableDefinition> {

  void execute(final Sql sql) throws Exception;

  List<CompletableFuture<DestinationInitialState<TableDefinition>>> gatherInitialState(List<StreamConfig> streamConfigs);

  boolean existingSchemaMatchesStreamConfig(StreamConfig streamConfig, TableDefinition tableDefinition);

}
