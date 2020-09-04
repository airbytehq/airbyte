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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.dataline.commons.json.Jsons;
import io.dataline.singer.SingerMessage;
import org.junit.jupiter.api.Test;

class SingerMessageTrackerTest {

  @Test
  public void testIncrementsWhenRecord() {
    final SingerMessage singerMessage = new SingerMessage();
    singerMessage.withType(SingerMessage.Type.RECORD);

    final SingerMessageTracker singerMessageTracker = new SingerMessageTracker();
    singerMessageTracker.accept(singerMessage);
    singerMessageTracker.accept(singerMessage);
    singerMessageTracker.accept(singerMessage);
    assertEquals(3, singerMessageTracker.getRecordCount());
  }

  @Test
  public void testRetainsLatestState() {
    final JsonNode oldStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598900000").build());
    final SingerMessage oldSingerMessage = new SingerMessage()
        .withType(SingerMessage.Type.STATE)
        .withValue(oldStateValue);

    final JsonNode newStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598993526").build());
    final SingerMessage newStateMessage = new SingerMessage()
        .withType(SingerMessage.Type.STATE)
        .withValue(newStateValue);

    final SingerMessageTracker singerMessageTracker = new SingerMessageTracker();
    singerMessageTracker.accept(oldSingerMessage);
    singerMessageTracker.accept(oldSingerMessage);
    singerMessageTracker.accept(newStateMessage);

    assertTrue(singerMessageTracker.getOutputState().isPresent());
    assertEquals(newStateValue, singerMessageTracker.getOutputState().get());
  }

  @Test
  public void testReturnEmptyStateIfNoneEverAccepted() {
    final SingerMessageTracker singerMessageTracker = new SingerMessageTracker();
    assertTrue(singerMessageTracker.getOutputState().isEmpty());
  }

}
