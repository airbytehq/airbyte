/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.time.Instant;
import java.util.Optional;

public class JdbcDestinationHandler implements DestinationHandler<JdbcDatabase> {

  public JdbcDestinationHandler() {

  }

  @Override
  public Optional<JdbcDatabase> findExistingTable(StreamId id) throws Exception {
    return Optional.empty();
  }

  @Override
  public boolean isFinalTableEmpty(StreamId id) throws Exception {
    return false;
  }

  @Override
  public Optional<Instant> getMinTimestampForSync(StreamId id) throws Exception {
    return Optional.empty();
  }

  @Override
  public void execute(String sql) throws Exception {

  }

}
