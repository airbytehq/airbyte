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

import io.dataline.commons.json.Jsons;
import io.dataline.singer.SingerMessage;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

@SuppressWarnings("StringBufferReplaceableByString")
class SingerJsonStreamFactoryTest {

  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";

  @Test
  public void testValid() {
    final SingerMessage record1 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "green");
    final SingerMessage record2 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final String inputString =
        new StringBuilder()
            .append(Jsons.serialize(record1))
            .append('\n')
            .append(Jsons.serialize(record2))
            .toString();

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(inputString);
    final Stream<SingerMessage> expectedStream = Stream.of(record1, record2);

    assertEquals(
        expectedStream.collect(Collectors.toList()), messageStream.collect(Collectors.toList()));
  }

  @Test
  public void testInvalid() {
    final SingerMessage record1 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "green");
    final SingerMessage record2 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final String inputString =
        new StringBuilder()
            .append(Jsons.serialize(record1))
            .append('\n')
            .append("{ \"fish\": \"tuna\"}")
            .append('\n')
            .append(Jsons.serialize(record2))
            .toString();

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(inputString);
    final Stream<SingerMessage> expectedStream = Stream.of(record1, record2);

    assertEquals(
        expectedStream.collect(Collectors.toList()), messageStream.collect(Collectors.toList()));
  }

  @Test
  public void testMissingNewLineBetweenValidRecords() {
    final SingerMessage record1 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "green");
    final SingerMessage record2 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final String inputString =
        new StringBuilder()
            .append(Jsons.serialize(record1))
            .append(Jsons.serialize(record2))
            .toString();

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(inputString);
    final Stream<SingerMessage> expectedStream = Stream.of(record1);

    assertEquals(
        expectedStream.collect(Collectors.toList()), messageStream.collect(Collectors.toList()));
  }

  @Test
  public void testMissingNewLineAndLineStartsWithValidRecord() {
    final SingerMessage record1 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "green");
    final SingerMessage record2 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final String inputString =
        new StringBuilder()
            .append(Jsons.serialize(record1))
            .append("{ \"fish\": \"tuna\"}")
            .append('\n')
            .append(Jsons.serialize(record2))
            .toString();

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(inputString);
    final Stream<SingerMessage> expectedStream = Stream.of(record1, record2);

    assertEquals(
        expectedStream.collect(Collectors.toList()), messageStream.collect(Collectors.toList()));
  }

  @Test
  public void testMissingNewLineAndLineStartsWithInvalidRecord() {
    final SingerMessage record1 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "green");
    final SingerMessage record2 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final String inputString =
        new StringBuilder()
             .append(Jsons.serialize(record1))
             .append('\n')
            .append("{ \"fish\": \"tuna\"}")
             .append(Jsons.serialize(record2))
            .toString();

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(inputString);
    final Stream<SingerMessage> expectedStream = Stream.of(record1);

    assertEquals(
        expectedStream.collect(Collectors.toList()), messageStream.collect(Collectors.toList()));
  }

  private static Stream<SingerMessage> stringToSingerMessageStream(String inputString) {
    InputStream inputStream = new ByteArrayInputStream(inputString.getBytes());
    final BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
    return new SingerJsonStreamFactory().create(bufferedReader);
  }

}
