package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

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

  @Override
  protected void assertStateMessagesForNewTableSnapshotTest(final List<AirbyteStateMessage> stateMessages,
      final AirbyteStateMessage stateMessageEmittedAfterFirstSyncCompletion) {
    assertEquals(7, stateMessages.size());
    for (int i = 0; i <= 4; i++) {
      final AirbyteStateMessage stateMessage = stateMessages.get(i);
      assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessage.getType());
      assertEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
          stateMessage.getGlobal().getSharedState());
      final Set<StreamDescriptor> streamsInSnapshotState = stateMessage.getGlobal().getStreamStates()
          .stream()
          .map(AirbyteStreamState::getStreamDescriptor)
          .collect(Collectors.toSet());
      assertEquals(2, streamsInSnapshotState.size());
      assertTrue(
          streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema())));
      assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA)));

      stateMessage.getGlobal().getStreamStates().forEach(s -> {
        final JsonNode streamState = s.getStreamState();
        if (s.getStreamDescriptor().equals(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema()))) {
          assertEquals("ctid", streamState.get("state_type").asText());
        } else if (s.getStreamDescriptor().equals(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA))) {
          assertFalse(streamState.has("state_type"));
        } else {
          throw new RuntimeException("Unknown stream");
        }
      });
    }

    final AirbyteStateMessage secondLastSateMessage = stateMessages.get(5);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, secondLastSateMessage.getType());
    assertEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
        secondLastSateMessage.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSnapshotState = secondLastSateMessage.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(2, streamsInSnapshotState.size());
    assertTrue(
        streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema())));
    assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA)));
    secondLastSateMessage.getGlobal().getStreamStates().forEach(s -> {
      final JsonNode streamState = s.getStreamState();
      assertFalse(streamState.has("state_type"));
    });

    final AirbyteStateMessage stateMessageEmittedAfterSecondSyncCompletion = stateMessages.get(6);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessageEmittedAfterSecondSyncCompletion.getType());
    assertNotEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
        stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSyncCompletionState = stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(2, streamsInSnapshotState.size());
    assertTrue(
        streamsInSyncCompletionState.contains(
            new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema())));
    assertTrue(streamsInSyncCompletionState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA)));
    assertNotNull(stateMessageEmittedAfterSecondSyncCompletion.getData());
  }

}
