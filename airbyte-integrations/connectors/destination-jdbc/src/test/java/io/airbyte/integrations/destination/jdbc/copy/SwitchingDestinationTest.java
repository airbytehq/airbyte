package io.airbyte.integrations.destination.jdbc.copy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Map;
import java.util.function.Function;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

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
                SwitchingEnum.COPY, copyDestination
        );
    }

    @Test
    public void testInsert() throws Exception {
        var switchingDestination = new SwitchingDestination<>(SwitchingEnum.class, c -> SwitchingEnum.INSERT, destinationMap);

        switchingDestination.getConsumer(mock(JsonNode.class), mock(ConfiguredAirbyteCatalog.class));

        verify(insertDestination, times(1)).getConsumer(any(), any());
        verify(copyDestination, times(0)).getConsumer(any(), any());

        switchingDestination.check(mock(JsonNode.class));

        verify(insertDestination, times(1)).check(any());
        verify(copyDestination, times(0)).check(any());
    }

    @Test
    public void testCopy() throws Exception {
        var switchingDestination = new SwitchingDestination<>(SwitchingEnum.class, c -> SwitchingEnum.COPY, destinationMap);

        switchingDestination.getConsumer(mock(JsonNode.class), mock(ConfiguredAirbyteCatalog.class));

        verify(insertDestination, times(0)).getConsumer(any(), any());
        verify(copyDestination, times(1)).getConsumer(any(), any());

        switchingDestination.check(mock(JsonNode.class));

        verify(insertDestination, times(0)).check(any());
        verify(copyDestination, times(1)).check(any());
    }
}