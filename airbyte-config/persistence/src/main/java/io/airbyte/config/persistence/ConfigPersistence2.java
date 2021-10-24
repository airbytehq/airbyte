/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.Tables.SYNC_STATE;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import java.io.IOException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import org.jooq.JSONB;
import org.jooq.Record1;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigPersistence2 {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigPersistence2.class);

  private final ExceptionWrappingDatabase configDatabase;
  private final Supplier<Instant> timeSupplier;

  public ConfigPersistence2(final Database configDatabase) {
    this(configDatabase, Instant::now);
  }

  @VisibleForTesting
  ConfigPersistence2(final Database configDatabase, final Supplier<Instant> timeSupplier) {
    this.configDatabase = new ExceptionWrappingDatabase(configDatabase);

    this.timeSupplier = timeSupplier;
  }

  public Optional<State> getCurrentState(final UUID connectionId) throws IOException {
    return configDatabase.query(ctx -> {
      final Record1<JSONB> record = ctx.select(SYNC_STATE.STATE)
          .from(SYNC_STATE)
          .where(SYNC_STATE.SYNC_ID.eq(connectionId))
          .fetchAny();
      if (record == null) {
        return Optional.empty();
      }

      return Optional.of(Jsons.deserialize(record.value1().data(), State.class));
    });
  }

  public void updateSyncState(final UUID connectionId, final State state) throws IOException {
    final OffsetDateTime now = OffsetDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    configDatabase.transaction(
        ctx -> {
          final boolean hasExistingRecord = ctx.fetchExists(SYNC_STATE, SYNC_STATE.SYNC_ID.eq(connectionId));
          if (hasExistingRecord) {
            LOGGER.info("Updating connection {} state", connectionId);
            return ctx.update(SYNC_STATE)
                .set(SYNC_STATE.STATE, JSONB.valueOf(Jsons.serialize(state)))
                .set(SYNC_STATE.UPDATED_AT, now)
                .where(SYNC_STATE.SYNC_ID.eq(connectionId))
                .execute();
          } else {
            LOGGER.info("Inserting new state for connection {}", connectionId);
            return ctx.insertInto(SYNC_STATE)
                .set(SYNC_STATE.SYNC_ID, connectionId)
                .set(SYNC_STATE.STATE, JSONB.valueOf(Jsons.serialize(state)))
                .set(SYNC_STATE.CREATED_AT, now)
                .set(SYNC_STATE.UPDATED_AT, now)
                .execute();
          }
        });
  }

}
