/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.STREAM_RESET;
import static org.jooq.impl.DSL.noCondition;

import io.airbyte.config.StreamResetRecord;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.protocol.models.StreamDescriptor;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Stream;
import org.jooq.Condition;
import org.jooq.DSLContext;
import org.jooq.Record;
import org.jooq.RecordMapper;
import org.jooq.impl.DSL;

public class StreamResetPersistence {

  private final ExceptionWrappingDatabase database;

  public StreamResetPersistence(final Database database) {
    this.database = new ExceptionWrappingDatabase(database);
  }

  /*
   * Get a list of StreamDescriptors for streams that have pending or running resets
   */
  public List<StreamDescriptor> getStreamResets(final UUID connectionId) throws IOException {
    return database.query(ctx -> ctx.select(DSL.asterisk())
        .from(STREAM_RESET))
        .where(STREAM_RESET.CONNECTION_ID.eq(connectionId))
        .fetch(getStreamResetRecordMapper())
        .stream()
        .flatMap(row -> Stream.of(new StreamDescriptor().withName(row.streamName()).withNamespace(row.streamNamespace())))
        .toList();
  }

  /*
   * Delete stream resets for a given connection. This is called to delete stream reset records for
   * resets that are successfully completed.
   */
  public void deleteStreamResets(final UUID connectionId, final List<StreamDescriptor> streamsToDelete) throws IOException {
    Condition condition = noCondition();
    for (final StreamDescriptor streamDescriptor : streamsToDelete) {
      condition = condition.or(
          STREAM_RESET.CONNECTION_ID.eq(connectionId)
              .and(STREAM_RESET.STREAM_NAME.eq(streamDescriptor.getName()))
              .and(PersistenceHelpers.isNullOrEquals(STREAM_RESET.STREAM_NAMESPACE, streamDescriptor.getNamespace())));
    }

    database.query(ctx -> ctx.deleteFrom(STREAM_RESET)).where(condition).execute();
  }

  /**
   * Create stream resets for a given connection. This is called to create stream reset records for
   * resets that are going to be run.
   *
   * It will not attempt to create entries for any stream that already exists in the stream_reset
   * table.
   */
  public void createStreamResets(final UUID connectionId, final List<StreamDescriptor> streamsToCreate) throws IOException {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    database.transaction(ctx -> {
      createStreamResets(ctx, connectionId, streamsToCreate, timestamp);
      return null;
    });
  }

  private void createStreamResets(final DSLContext ctx,
                                  final UUID connectionId,
                                  final List<StreamDescriptor> streamsToCreate,
                                  final OffsetDateTime timestamp) {
    for (final StreamDescriptor streamDescriptor : streamsToCreate) {
      final boolean streamExists = ctx.fetchExists(
          STREAM_RESET,
          STREAM_RESET.CONNECTION_ID.eq(connectionId),
          STREAM_RESET.STREAM_NAME.eq(streamDescriptor.getName()),
          PersistenceHelpers.isNullOrEquals(STREAM_RESET.STREAM_NAMESPACE, streamDescriptor.getNamespace()));

      if (!streamExists) {
        ctx.insertInto(STREAM_RESET)
            .set(STREAM_RESET.ID, UUID.randomUUID())
            .set(STREAM_RESET.CONNECTION_ID, connectionId)
            .set(STREAM_RESET.STREAM_NAME, streamDescriptor.getName())
            .set(STREAM_RESET.STREAM_NAMESPACE, streamDescriptor.getNamespace())
            .set(STREAM_RESET.CREATED_AT, timestamp)
            .set(STREAM_RESET.UPDATED_AT, timestamp)
            .execute();
      }
    }
  }

  private static RecordMapper<Record, StreamResetRecord> getStreamResetRecordMapper() {
    return record -> new StreamResetRecord(
        UUID.fromString(record.get(STREAM_RESET.CONNECTION_ID, String.class)),
        record.get(STREAM_RESET.STREAM_NAME, String.class),
        record.get(STREAM_RESET.STREAM_NAMESPACE, String.class));
  }

}
