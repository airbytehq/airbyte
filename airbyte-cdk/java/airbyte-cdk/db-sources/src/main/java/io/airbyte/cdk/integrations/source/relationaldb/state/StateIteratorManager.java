package io.airbyte.cdk.integrations.source.relationaldb.state;

import io.airbyte.cdk.integrations.source.relationaldb.StateDecoratingIterator;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.time.Instant;
import java.util.Iterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class StateIteratorManager implements SourceStateIteratorManager<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(StateIteratorManager.class);

  private final Iterator<AirbyteMessage> messageIterator;
  private final StateManager stateManager;
  private final AirbyteStreamNameNamespacePair pair;
  private final String cursorField;
  private final JsonSchemaPrimitive cursorType;

  private final String initialCursor;
  private String currentMaxCursor;
  private long currentMaxCursorRecordCount = 0L;
  private boolean hasEmittedFinalState;
  private final int stateEmissionFrequency;
  private int totalRecordCount = 0;
  // In between each state message, recordCountInStateMessage will be reset to 0.
  private int recordCountInStateMessage = 0;
  private boolean emitIntermediateState = false;
  private AirbyteMessage intermediateStateMessage = null;
  private boolean hasCaughtException = false;

  public StateIteratorManager(final Iterator<AirbyteMessage> messageIterator,
      final StateManager stateManager,
      final AirbyteStreamNameNamespacePair pair,
      final String cursorField,
      final String initialCursor,
      final JsonSchemaPrimitive cursorType,
      final int stateEmissionFrequency) {
    this.messageIterator = messageIterator;
    this.stateManager = stateManager;
    this.pair = pair;
    this.cursorField = cursorField;
    this.cursorType = cursorType;
    this.initialCursor = initialCursor;
    this.currentMaxCursor = initialCursor;
    this.stateEmissionFrequency = stateEmissionFrequency;
  }

  /**
   * @return
   */
  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint() {
    return null;
  }

  /**
   * @param message
   * @return
   */
  @Override
  public AirbyteMessage processRecordMessage(AirbyteMessage message) {
    return null;
  }

  /**
   * @return
   */
  @Override
  public AirbyteStateMessage createFinalStateMessage() {
    return null;
  }

  /**
   * @param recordCount
   * @param lastCheckpoint
   * @return
   */
  @Override
  public boolean shouldEmitStateMessage(long recordCount, Instant lastCheckpoint) {
    return stateEmissionFrequency > 0 && totalRecordCount % stateEmissionFrequency == 0;
  }
}
