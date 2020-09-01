/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers.protocol.singer;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.dataline.commons.json.Jsons;
import io.dataline.config.SingerMessage;
import io.dataline.config.State;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class SingerMessageTrackerTest {

  @Test
  public void testIncrementsWhenRecord() {
    final SingerMessage singerMessage = new SingerMessage();
    singerMessage.setType(SingerMessage.Type.RECORD);
    singerMessage.setRecord(Jsons.jsonNode(ImmutableMap.builder().put("like", "true").put("userId", "123").build()));

    final UUID connectionId = UUID.randomUUID();
    final SingerMessageTracker singerMessageTracker = new SingerMessageTracker(connectionId);
    singerMessageTracker.accept(singerMessage);
    singerMessageTracker.accept(singerMessage);
    singerMessageTracker.accept(singerMessage);
    assertEquals(3, singerMessageTracker.getRecordCount());
  }

  @Test
  public void testRetainsLatestStateWhenState() {
    final JsonNode oldStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598900000").build());
    final JsonNode newStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598993526").build());
    final SingerMessage oldSingerMessage = new SingerMessage();
    oldSingerMessage.setType(SingerMessage.Type.STATE);
    oldSingerMessage.setValue(oldStateValue);

    final SingerMessage newStateMessage = new SingerMessage();
    newStateMessage.setType(SingerMessage.Type.STATE);
    newStateMessage.setValue(newStateValue);

    final UUID connectionId = UUID.randomUUID();
    final SingerMessageTracker singerMessageTracker = new SingerMessageTracker(connectionId);
    singerMessageTracker.accept(oldSingerMessage);
    singerMessageTracker.accept(oldSingerMessage);
    singerMessageTracker.accept(newStateMessage);

    final State expectedState = new State();
    expectedState.setConnectionId(connectionId);
    expectedState.setState(newStateValue);

    assertTrue(singerMessageTracker.getOutputState().isPresent());
    assertEquals(expectedState, singerMessageTracker.getOutputState().get());
  }

  @Test
  public void testNoStateIfNoneEverAccepted() {
    final UUID connectionId = UUID.randomUUID();
    final SingerMessageTracker singerMessageTracker = new SingerMessageTracker(connectionId);
    assertTrue(singerMessageTracker.getOutputState().isEmpty());
  }

}
