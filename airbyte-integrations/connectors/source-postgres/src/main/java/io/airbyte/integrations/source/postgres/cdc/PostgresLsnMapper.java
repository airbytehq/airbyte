/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import static io.debezium.connector.postgresql.PostgresOffsetContext.LAST_COMMIT_LSN_KEY;
import static io.debezium.connector.postgresql.PostgresOffsetContext.LAST_COMPLETELY_PROCESSED_LSN_KEY;
import static io.debezium.connector.postgresql.SourceInfo.LSN_KEY;

import com.google.common.base.Preconditions;
import io.airbyte.cdk.components.debezium.DebeziumRecord;
import io.airbyte.cdk.components.debezium.DebeziumState;
import io.airbyte.cdk.components.debezium.LsnMapper;
import io.airbyte.cdk.db.PgLsn;
import org.apache.kafka.connect.source.SourceRecord;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class PostgresLsnMapper implements LsnMapper<PgLsn> {

  @NotNull
  @Override
  public PgLsn get(@NotNull DebeziumState.Offset offset) {
    Preconditions.checkState(offset.debeziumOffset().size() == 1);
    var json = offset.debeziumOffset().values().iterator().next();
    if (json.has(LSN_KEY)) {
      return PgLsn.fromLong(json.get(LSN_KEY).asLong());
    }
    if (json.has(LAST_COMPLETELY_PROCESSED_LSN_KEY)) {
      return PgLsn.fromLong(json.get(LAST_COMPLETELY_PROCESSED_LSN_KEY).asLong());
    }
    if (json.has(LAST_COMMIT_LSN_KEY)) {
      return PgLsn.fromLong(json.get(LAST_COMMIT_LSN_KEY).asLong());
    }
    throw new IllegalStateException("debezium offset has no known LSN data: " + offset);
  }

  @Nullable
  @Override
  public PgLsn get(@NotNull DebeziumRecord record) {
    if (!record.source().has("lsn")) {
      return null;
    }
    return PgLsn.fromLong(record.source().get("lsn").asLong());
  }

  @Nullable
  @Override
  public PgLsn get(@NotNull SourceRecord sourceRecord) {
    final Object lsnValue = sourceRecord.sourceOffset().get("lsn");
    if (lsnValue instanceof Long) {
      return PgLsn.fromLong((Long) lsnValue);
    }
    return null;
  }

}
