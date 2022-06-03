/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.jooq.impl.DSL.noCondition;

import io.airbyte.config.StreamKey;
import io.airbyte.config.StreamResetRecord;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.Condition;
import org.jooq.Field;
import org.jooq.Record;
import org.jooq.RecordMapper;
import org.jooq.Table;
import org.jooq.impl.DSL;

public class StreamResetPersistence {

  private static final String STREAM_RESET_TABLE = "stream_reset";
  private static final String CONNECTION_ID_COL = "connection_id";
  private static final String STREAM_NAME_COL = "stream_name";
  private static final String STREAM_NAMESPACE_COL = "stream_namespace";
  private static final Field<Object> DSL_FIELD_STREAM_NAME = DSL.field(STREAM_NAME_COL);
  private static final Table<Record> DSL_TABLE_STREAM_RESET = DSL.table(STREAM_RESET_TABLE);

  private static final String UPDATED_AT_COL = "updated_at";

  private final ExceptionWrappingDatabase database;

  public StreamResetPersistence(final Database database) {
    this.database = new ExceptionWrappingDatabase(database);
  }

  public List<StreamKey> getStreamResets(final UUID connectionId) throws IOException {
    return database.query(ctx -> ctx.select(DSL.asterisk())
        .from(DSL_TABLE_STREAM_RESET))
        .where(DSL.field(CONNECTION_ID_COL).eq(connectionId))
        .fetch(getStreamResetRecordMapper())
        .stream()
        .flatMap(row -> Stream.of(new StreamKey().withName(row.streamName()).withNamespace(row.streamNamespace())))
        .collect(Collectors.toList());
  }

  public void deleteStreamResets(final UUID connectionId, final List<StreamKey> streamsToDelete) throws IOException {
    final Condition condition = noCondition();
    for (final StreamKey streamKey : streamsToDelete) {
      condition.or(DSL.field(CONNECTION_ID_COL).eq(connectionId).and(DSL.field(STREAM_NAME_COL).eq(streamKey.getName()))
          .and(DSL.field(STREAM_NAMESPACE_COL).eq(streamKey.getNamespace())));
    }

    database.query(ctx -> ctx.deleteFrom(DSL_TABLE_STREAM_RESET)).where(condition);
  }

  private static RecordMapper<Record, StreamResetRecord> getStreamResetRecordMapper() {
    return record -> new StreamResetRecord(
        UUID.fromString(record.get(CONNECTION_ID_COL, String.class)),
        record.get(STREAM_NAME_COL, String.class),
        record.get(STREAM_NAMESPACE_COL, String.class),
        record.get(UPDATED_AT_COL, Instant.class));
  }

}
