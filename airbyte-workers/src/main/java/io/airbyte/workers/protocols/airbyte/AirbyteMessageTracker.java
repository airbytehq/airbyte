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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Charsets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.protocols.MessageTracker;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;

public class AirbyteMessageTracker implements MessageTracker<AirbyteMessage> {

  private final AtomicLong recordCount;
  private final AtomicLong numBytes;
  private final AtomicReference<JsonNode> outputState;

  public AirbyteMessageTracker() {
    this.recordCount = new AtomicLong();
    this.numBytes = new AtomicLong();
    this.outputState = new AtomicReference<>();
  }

  @Override
  public void accept(AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      recordCount.incrementAndGet();
      // todo (cgardens) - pretty wasteful to do an extra serialization just to get size.
      numBytes.addAndGet(Jsons.serialize(message.getRecord().getData()).getBytes(Charsets.UTF_8).length);
    }
    if (message.getType() == AirbyteMessage.Type.STATE) {
      outputState.set(message.getState().getData());
    }
  }

  public long getRecordCount() {
    return recordCount.get();
  }

  public long getBytesCount() {
    return numBytes.get();
  }

  public Optional<JsonNode> getOutputState() {
    return Optional.ofNullable(outputState.get());
  }

}
