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

import com.fasterxml.jackson.databind.JsonNode;
import io.dataline.singer.SingerMessage;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;

public class SingerMessageTracker implements Consumer<SingerMessage> {

  private final AtomicLong recordCount;
  private final AtomicReference<JsonNode> outputState;

  public SingerMessageTracker() {
    this.recordCount = new AtomicLong();
    this.outputState = new AtomicReference<>();
  }

  @Override
  public void accept(SingerMessage message) {
    if (message.getType().equals(SingerMessage.Type.RECORD)) {
      recordCount.incrementAndGet();
    }
    if (message.getType().equals(SingerMessage.Type.STATE)) {
      outputState.set(message.getValue());
    }
  }

  public long getRecordCount() {
    return recordCount.get();
  }

  public Optional<JsonNode> getOutputState() {
    return Optional.ofNullable(outputState.get());
  }

}
