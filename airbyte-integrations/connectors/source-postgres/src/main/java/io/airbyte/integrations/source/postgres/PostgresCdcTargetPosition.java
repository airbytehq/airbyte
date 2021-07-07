/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.postgres;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.PgLsn;
import io.airbyte.db.PostgresUtils;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.debezium.SnapshotMetadata;
import io.airbyte.integrations.source.debezium.interfaces.CdcTargetPosition;
import io.debezium.engine.ChangeEvent;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.sql.SQLException;
import java.util.Optional;
import org.apache.kafka.connect.data.Struct;
import org.apache.kafka.connect.source.SourceRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCdcTargetPosition implements CdcTargetPosition {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCdcTargetPosition.class);
  private final PgLsn targetLsn;

  public PostgresCdcTargetPosition(PgLsn targetLsn) {
    this.targetLsn = targetLsn;
  }

  @Override
  public boolean equals(Object obj) {
    if (obj instanceof PostgresCdcTargetPosition) {
      PostgresCdcTargetPosition cdcTargetPosition = (PostgresCdcTargetPosition) obj;
      return cdcTargetPosition.targetLsn.compareTo(targetLsn) == 0;
    }
    return false;
  }

  static PostgresCdcTargetPosition targetPosition(JdbcDatabase database) {
    try {
      PgLsn lsn = PostgresUtils.getLsn(database);
      LOGGER.info("identified target lsn: " + lsn);
      return new PostgresCdcTargetPosition(lsn);
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public boolean reachedTargetPosition(ChangeEvent<String, String> event) {
    final PgLsn eventLsn = extractLsn(event);

    if (targetLsn.compareTo(eventLsn) > 0) {
      return false;
    } else {
      final SnapshotMetadata snapshotMetadata = getSnapshotMetadata(event);
      // if not snapshot or is snapshot but last record in snapshot.
      return SnapshotMetadata.TRUE != snapshotMetadata;
    }
  }

  private SnapshotMetadata getSnapshotMetadata(ChangeEvent<String, String> event) {
    try {
      /*
       * Debezium emits EmbeddedEngineChangeEvent, but that class is not public and it is hidden behind
       * the ChangeEvent iface. The EmbeddedEngineChangeEvent contains the information about whether the
       * record was emitted in snapshot mode or not, which we need to determine whether to stop producing
       * records or not. Thus we use reflection to access that hidden information.
       */
      final Method sourceRecordMethod = event.getClass().getMethod("sourceRecord");
      sourceRecordMethod.setAccessible(true);
      final SourceRecord sourceRecord = (SourceRecord) sourceRecordMethod.invoke(event);
      final String snapshot = ((Struct) sourceRecord.value()).getStruct("source").getString("snapshot");

      if (snapshot == null) {
        return null;
      }

      // the snapshot field is an enum of true, false, and last.
      return SnapshotMetadata.valueOf(snapshot.toUpperCase());
    } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
      throw new RuntimeException(e);
    }
  }

  private PgLsn extractLsn(ChangeEvent<String, String> event) {
    return Optional.ofNullable(event.value())
        .flatMap(value -> Optional.ofNullable(Jsons.deserialize(value).get("source")))
        .flatMap(source -> Optional.ofNullable(source.get("lsn").asText()))
        .map(Long::parseLong)
        .map(PgLsn::fromLong)
        .orElseThrow(() -> new IllegalStateException("Could not find LSN"));
  }

}
