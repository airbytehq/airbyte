package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.PgLsn;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;

public class CtidEnabledCdcPostgresSourceTest extends CdcPostgresSourceTest {

  @Override
  protected void assertStateForSyncShouldHandlePurgedLogsGracefully(final List<AirbyteStateMessage> stateMessages, final int syncNumber) {
    if (syncNumber == 1) {
      assertEquals(7, stateMessages.size());
    } else if (syncNumber == 3) {
      assertEquals(28, stateMessages.size());
    } else {
      throw new RuntimeException("Unknown sync number " + syncNumber);
    }
  }

  @Override
  protected void assertLsnPositionForSyncShouldIncrementLSN(final Long lsnPosition1,
      final Long lsnPosition2, final int syncNumber) {
    if (syncNumber == 1) {
      assertEquals(1, lsnPosition2.compareTo(lsnPosition1));
    } else if (syncNumber == 2) {
      assertEquals(0, lsnPosition2.compareTo(lsnPosition1));
    } else {
      throw new RuntimeException("Unknown sync number " + syncNumber);
    }
  }

  @Override
  protected void assertStateForVerifyCheckpointStatesByRecords(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(7, stateMessages.size());
  }

}
