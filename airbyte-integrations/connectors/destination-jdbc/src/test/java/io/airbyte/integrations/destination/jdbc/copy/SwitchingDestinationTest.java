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

package io.airbyte.integrations.destination.jdbc.copy;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
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
    var switchingDestination = new SwitchingDestination<>(SwitchingEnum.class, c -> SwitchingEnum.INSERT, destinationMap);

    switchingDestination.getConsumer(mock(JsonNode.class), mock(ConfiguredAirbyteCatalog.class), mock(Consumer.class));

    verify(insertDestination, times(1)).getConsumer(any(), any(), any());
    verify(copyDestination, times(0)).getConsumer(any(), any(), any());

    switchingDestination.check(mock(JsonNode.class));

    verify(insertDestination, times(1)).check(any());
    verify(copyDestination, times(0)).check(any());
  }

  @Test
  public void testCopy() throws Exception {
    var switchingDestination = new SwitchingDestination<>(SwitchingEnum.class, c -> SwitchingEnum.COPY, destinationMap);

    switchingDestination.getConsumer(mock(JsonNode.class), mock(ConfiguredAirbyteCatalog.class), mock(Consumer.class));

    verify(insertDestination, times(0)).getConsumer(any(), any(), any());
    verify(copyDestination, times(1)).getConsumer(any(), any(), any());

    switchingDestination.check(mock(JsonNode.class));

    verify(insertDestination, times(0)).check(any());
    verify(copyDestination, times(1)).check(any());
  }

}
