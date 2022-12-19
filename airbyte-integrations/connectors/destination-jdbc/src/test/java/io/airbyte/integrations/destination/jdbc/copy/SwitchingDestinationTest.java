/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SwitchingDestinationTest {

  enum SwitchingEnum {
    INSERT,
    COPY
  }

  private Destination insertDestination;
  private Destination copyDestination;
  private Map<SwitchingEnum, Destination> destinationMap;

  @BeforeEach
  public void setUp() {
    insertDestination = mock(Destination.class);
    copyDestination = mock(Destination.class);
    destinationMap = ImmutableMap.of(
        SwitchingEnum.INSERT, insertDestination,
        SwitchingEnum.COPY, copyDestination);
  }

  @Test
  public void testInsert() throws Exception {
    final var switchingDestination = new SwitchingDestination<>(SwitchingEnum.class, c -> SwitchingEnum.INSERT, destinationMap);

    switchingDestination.getConsumer(mock(JsonNode.class), mock(ConfiguredAirbyteCatalog.class), mock(Consumer.class));

    verify(insertDestination, times(1)).getConsumer(any(), any(), any());
    verify(copyDestination, times(0)).getConsumer(any(), any(), any());

    switchingDestination.check(mock(JsonNode.class));

    verify(insertDestination, times(1)).check(any());
    verify(copyDestination, times(0)).check(any());
  }

  @Test
  public void testCopy() throws Exception {
    final var switchingDestination = new SwitchingDestination<>(SwitchingEnum.class, c -> SwitchingEnum.COPY, destinationMap);

    switchingDestination.getConsumer(mock(JsonNode.class), mock(ConfiguredAirbyteCatalog.class), mock(Consumer.class));

    verify(insertDestination, times(0)).getConsumer(any(), any(), any());
    verify(copyDestination, times(1)).getConsumer(any(), any(), any());

    switchingDestination.check(mock(JsonNode.class));

    verify(insertDestination, times(0)).check(any());
    verify(copyDestination, times(1)).check(any());
  }

}
