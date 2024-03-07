/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import static io.debezium.connector.postgresql.PostgresOffsetContext.LAST_COMMIT_LSN_KEY;
import static io.debezium.connector.postgresql.PostgresOffsetContext.LAST_COMPLETELY_PROCESSED_LSN_KEY;
import static io.debezium.connector.postgresql.SourceInfo.LSN_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.components.debezium.DebeziumComponent;
import io.airbyte.cdk.db.PgLsn;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.apache.kafka.connect.source.SourceRecord;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.postgresql.core.BaseConnection;
import org.postgresql.replication.LogSequenceNumber;
import org.postgresql.replication.PGReplicationStream;
import org.postgresql.replication.fluent.logical.ChainedLogicalStreamBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresLsnMapper implements DebeziumComponent.Config.LsnMapper<PgLsn> {

  @NotNull
  @Override
  public PgLsn get(@NotNull DebeziumComponent.State.Offset offset) {
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
  public PgLsn get(@NotNull DebeziumComponent.Record record) {
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
