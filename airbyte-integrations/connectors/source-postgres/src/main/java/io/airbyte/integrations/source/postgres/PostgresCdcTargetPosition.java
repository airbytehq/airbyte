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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.PgLsn;
import io.airbyte.db.PostgresUtils;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.integrations.debezium.internals.SnapshotMetadata;
import java.sql.SQLException;
import java.util.Objects;
import java.util.Optional;
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

  @Override
  public int hashCode() {
    return Objects.hash(targetLsn.asLong());
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
  public boolean reachedTargetPosition(JsonNode valueAsJson) {
    final PgLsn eventLsn = extractLsn(valueAsJson);

    if (targetLsn.compareTo(eventLsn) > 0) {
      return false;
    } else {
      SnapshotMetadata snapshotMetadata = SnapshotMetadata.valueOf(valueAsJson.get("source").get("snapshot").asText().toUpperCase());
      // if not snapshot or is snapshot but last record in snapshot.
      return SnapshotMetadata.TRUE != snapshotMetadata;
    }
  }

  private PgLsn extractLsn(JsonNode valueAsJson) {
    return Optional.ofNullable(valueAsJson.get("source"))
        .flatMap(source -> Optional.ofNullable(source.get("lsn").asText()))
        .map(Long::parseLong)
        .map(PgLsn::fromLong)
        .orElseThrow(() -> new IllegalStateException("Could not find LSN"));
  }

}
