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

package io.airbyte.workers.protocols.airbyte;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.base.Charsets;

class AirbyteMessageTrackerTest {

  @Test
  public void testIncrementsWhenRecord() {
    final AirbyteMessage message = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withData(Jsons.jsonNode(ImmutableMap.of("name", "rudolph"))));

    final AirbyteMessageTracker messageTracker = new AirbyteMessageTracker();
    messageTracker.accept(message);
    messageTracker.accept(message);
    messageTracker.accept(message);

    assertEquals(3, messageTracker.getRecordCount());
    assertEquals(3 * Jsons.serialize(message.getRecord().getData()).getBytes(Charsets.UTF_8).length, messageTracker.getBytesCount());
  }

  @Test
  public void testRetainsLatestState() {
    final JsonNode oldStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598900000").build());
    final AirbyteMessage oldStateMessage = new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(oldStateValue));

    final JsonNode newStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598993526").build());
    final AirbyteMessage newStateMessage = new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(newStateValue));

    final AirbyteMessageTracker messageTracker = new AirbyteMessageTracker();
    messageTracker.accept(oldStateMessage);
    messageTracker.accept(oldStateMessage);
    messageTracker.accept(newStateMessage);

    assertTrue(messageTracker.getOutputState().isPresent());
    assertEquals(newStateValue, messageTracker.getOutputState().get());
  }

  @Test
  public void testReturnEmptyStateIfNoneEverAccepted() {
    final AirbyteMessageTracker MessageTracker = new AirbyteMessageTracker();
    assertTrue(MessageTracker.getOutputState().isEmpty());
  }

}
