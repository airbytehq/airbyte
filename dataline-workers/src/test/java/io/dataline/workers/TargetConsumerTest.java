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

package io.dataline.workers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import io.dataline.commons.json.Jsons;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.protocol.singer.MessageUtils;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.StringWriter;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

@SuppressWarnings("StringBufferReplaceableByString")
public class TargetConsumerTest {

  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";

  @Test
  public void test() throws IOException {
    final SingerMessage record1 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "green");
    final SingerMessage record2 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final String expected =
        new StringBuilder()
            .append(Jsons.serialize(record1))
            .append('\n')
            .append(Jsons.serialize(record2))
            .append('\n')
            .toString();

    final Process processMock = mock(Process.class);
    final StringWriter stringWriter = new StringWriter();
    final BufferedWriter bufferedWriter = new BufferedWriter(stringWriter);

    final TargetConsumer targetConsumer = new TargetConsumer(bufferedWriter, processMock);

    final Stream<SingerMessage> recordStream = Stream.of(record1, record2);
    recordStream.forEach(targetConsumer);
    targetConsumer.close();

    final String actual = stringWriter.getBuffer().toString();
    assertEquals(expected, actual);

    verify(processMock).destroy();
  }

}
