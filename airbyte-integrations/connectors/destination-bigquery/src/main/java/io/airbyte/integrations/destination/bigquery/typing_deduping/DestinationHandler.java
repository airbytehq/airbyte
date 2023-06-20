/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.StreamId;
import java.util.Optional;

public interface DestinationHandler<DialectTableDefinition> {

  Optional<DialectTableDefinition> findExistingTable(StreamId id);

  void execute(String sql) throws Exception;

}
