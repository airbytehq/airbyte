/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.util.Optional;

public class JdbcDestinationHandler implements DestinationHandler<JdbcDatabase> {

  @Override
  public Optional<JdbcDatabase> findExistingTable(final StreamId id) throws Exception {
    return Optional.empty();
  }

  @Override
  public boolean isFinalTableEmpty(final StreamId id) throws Exception {
    return false;
  }

  @Override
  public void execute(final String sql) throws Exception {

  }

}
