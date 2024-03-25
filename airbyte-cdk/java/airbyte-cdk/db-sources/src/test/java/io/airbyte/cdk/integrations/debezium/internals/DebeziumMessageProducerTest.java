/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.cdk.integrations.debezium.CdcStateHandler;
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DebeziumMessageProducerTest {

  private DebeziumMessageProducer producer;

  CdcStateHandler cdcStateHandler;
  CdcTargetPosition targetPosition;
  DebeziumEventConverter eventConverter;
  AirbyteFileOffsetBackingStore offsetManager;
  AirbyteSchemaHistoryStorage schemaHistoryManager;

  private static Map<String, String> OFFSET_MANAGER_READ = new HashMap<>(Map.of("key", "value"));
  private static Map<String, String> OFFSET_MANAGER_READ2 = new HashMap<>(Map.of("key2", "value2"));

  private static AirbyteSchemaHistoryStorage.SchemaHistory SCHEMA = new AirbyteSchemaHistoryStorage.SchemaHistory("schema", false);

  private static AirbyteStateMessage STATE_MESSAGE = new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL);

  @BeforeEach
  void setUp() {
    cdcStateHandler = mock(CdcStateHandler.class);
    when(cdcStateHandler.isCdcCheckpointEnabled()).thenReturn(true);
    targetPosition = mock(CdcTargetPosition.class);
    eventConverter = mock(DebeziumEventConverter.class);
    offsetManager = mock(AirbyteFileOffsetBackingStore.class);
    when(offsetManager.read()).thenReturn(OFFSET_MANAGER_READ);
    schemaHistoryManager = mock(AirbyteSchemaHistoryStorage.class);
    when(schemaHistoryManager.read()).thenReturn(SCHEMA);
    producer = new DebeziumMessageProducer(cdcStateHandler, targetPosition, eventConverter, offsetManager, Optional.of(schemaHistoryManager));
  }

  @Test
  void testProcessRecordMessage() {
    ChangeEventWithMetadata message = mock(ChangeEventWithMetadata.class);

    when(targetPosition.isSameOffset(any(), any())).thenReturn(true);
    producer.processRecordMessage(null, message);
    verify(eventConverter).toAirbyteMessage(message);
    assertFalse(producer.shouldEmitStateMessage(null));
  }

  @Test
  void testProcessRecordMessageWithStateMessage() {
    ChangeEventWithMetadata message = mock(ChangeEventWithMetadata.class);

    when(targetPosition.isSameOffset(any(), any())).thenReturn(false);
    when(targetPosition.isEventAheadOffset(OFFSET_MANAGER_READ, message)).thenReturn(true);
    producer.processRecordMessage(null, message);
    verify(eventConverter).toAirbyteMessage(message);
    assertTrue(producer.shouldEmitStateMessage(null));

    when(cdcStateHandler.isCdcCheckpointEnabled()).thenReturn(false);
    when(cdcStateHandler.saveState(eq(OFFSET_MANAGER_READ), eq(SCHEMA))).thenReturn(new AirbyteMessage().withState(STATE_MESSAGE));

    assertEquals(producer.generateStateMessageAtCheckpoint(null), STATE_MESSAGE);
  }

  @Test
  void testGenerateFinalMessageNoProgress() {
    when(cdcStateHandler.saveState(eq(OFFSET_MANAGER_READ), eq(SCHEMA))).thenReturn(new AirbyteMessage().withState(STATE_MESSAGE));

    // initialOffset will be OFFSET_MANAGER_READ, final state would be OFFSET_MANAGER_READ2.
    // Mock CDC handler will only accept OFFSET_MANAGER_READ.
    when(offsetManager.read()).thenReturn(OFFSET_MANAGER_READ2);

    when(targetPosition.isSameOffset(OFFSET_MANAGER_READ, OFFSET_MANAGER_READ2)).thenReturn(true);

    assertEquals(producer.createFinalStateMessage(null), STATE_MESSAGE);
  }

  @Test
  void testGenerateFinalMessageWithProgress() {
    when(cdcStateHandler.saveState(eq(OFFSET_MANAGER_READ2), eq(SCHEMA))).thenReturn(new AirbyteMessage().withState(STATE_MESSAGE));

    // initialOffset will be OFFSET_MANAGER_READ, final state would be OFFSET_MANAGER_READ2.
    // Mock CDC handler will only accept OFFSET_MANAGER_READ2.
    when(offsetManager.read()).thenReturn(OFFSET_MANAGER_READ2);
    when(targetPosition.isSameOffset(OFFSET_MANAGER_READ, OFFSET_MANAGER_READ2)).thenReturn(false);

    assertEquals(producer.createFinalStateMessage(null), STATE_MESSAGE);
  }

}
