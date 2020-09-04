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

import io.dataline.commons.json.Jsons;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.StreamFactory;
import java.io.BufferedReader;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Creates a stream from an input stream. The produced stream attempts to parse each line of the
 * InputStream into a SingerMessage. If the line cannot be parsed into a SingerMessage it is
 * dropped. Each record MUST be new line separated.
 *
 * <p>
 * If a line starts with a SingerMessage and then has other characters after it, that SingerMessage
 * will still be parsed. If there are multiple SingerMessage records on the same line, only the
 * first will be parsed.
 */
public class SingerJsonStreamFactory implements StreamFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerJsonStreamFactory.class);

  public Stream<SingerMessage> create(BufferedReader bufferedReader) {
    return bufferedReader.lines().map(this::parseJsonOrNull).filter(Objects::nonNull);
  }

  private SingerMessage parseJsonOrNull(String record) {
    Optional<SingerMessage> message = Jsons.tryDeserialize(record, SingerMessage.class);
    if (message.isPresent()) {
      return message.get();
    } else {
      LOGGER.info("Record was not a json representation of a SingerMessage. Record: {}", record);
      return null;
    }
  }

}
