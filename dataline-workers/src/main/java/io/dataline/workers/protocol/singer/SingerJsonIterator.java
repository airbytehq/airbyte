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

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.AbstractIterator;
import io.dataline.config.SingerMessage;
import java.io.IOException;
import java.io.InputStream;

public class SingerJsonIterator extends AbstractIterator<SingerMessage> {
  private final ObjectMapper objectMapper;
  private final JsonParser jsonParser;
  private boolean hasReadFirstToken = false;

  // https://cassiomolin.com/2019/08/19/combining-jackson-streaming-api-with-objectmapper-for-parsing-json/
  public SingerJsonIterator(InputStream inputStream) {
    this.objectMapper = new ObjectMapper();
    try {
      this.jsonParser = objectMapper.getFactory().createParser(inputStream);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected SingerMessage computeNext() {
    if (!hasReadFirstToken) {
      checkInputStreamIsJson();
      hasReadFirstToken = true;
    }
    try {
      if (jsonParser.nextToken() != JsonToken.END_ARRAY) {
        return endOfData();
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    try {
      return objectMapper.readValue(jsonParser, SingerMessage.class);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private void checkInputStreamIsJson() {
    try {
      // Check the first token
      if (jsonParser.nextToken() != JsonToken.START_ARRAY) {
        throw new IllegalStateException("Expected content to be an array");
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }
}
