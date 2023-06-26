package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.List;

public class CtidEnabledCdcPostgresSourceTest extends CdcPostgresSourceTest {

  @Override
  protected void assertStateForSyncShouldHandlePurgedLogsGracefully(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(28, stateMessages.size());
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
  protected void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(7, stateMessages.size());
  }

  @Override
  protected void assertExpectedStateMessagesFromIncrementalSync(final List<AirbyteStateMessage> stateMessages) {
    super.assertExpectedStateMessages(stateMessages);
  }

  @Override
  protected void assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(final List<AirbyteStateMessage> stateAfterFirstBatch) {
    assertEquals(27, stateAfterFirstBatch.size());
  }

  @Override
  protected void assertExpectedStateMessagesForNoData(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(2, stateMessages.size());
  }

}
