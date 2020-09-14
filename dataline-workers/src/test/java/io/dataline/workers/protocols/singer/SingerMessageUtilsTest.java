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

package io.dataline.workers.protocols.singer;

import static org.junit.jupiter.api.Assertions.*;

import io.dataline.commons.json.Jsons;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.protocols.singer.SingerMessageUtils;
import java.time.Instant;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class SingerMessageUtilsTest {

  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";
  private static final String COLUMN_VALUE = "aubergine";

  @Test
  public void testCreateRecordMessageWithJsonNode() {
    final Instant now = Instant.now();
    final SingerMessage expectedMessage = new SingerMessage()
        .withType(SingerMessage.Type.RECORD)
        .withStream(TABLE_NAME)
        .withRecord(Jsons.jsonNode(ImmutableMap.of(COLUMN_NAME, COLUMN_VALUE)))
        .withTimeExtracted(SingerMessageUtils.SINGER_DATETIME_FORMATTER.format(now));

    final SingerMessage actualMessage = SingerMessageUtils.createRecordMessage(
        TABLE_NAME,
        Jsons.jsonNode(ImmutableMap.of(COLUMN_NAME, COLUMN_VALUE)),
        now);

    assertEquals(expectedMessage, actualMessage);
  }

  @Test
  public void testCreateRecordMessageWithMap() {
    final SingerMessage expectedMessage = new SingerMessage()
        .withType(SingerMessage.Type.RECORD)
        .withStream(TABLE_NAME)
        .withRecord(Jsons.jsonNode(ImmutableMap.of(COLUMN_NAME, COLUMN_VALUE)));

    final SingerMessage actualMessage = SingerMessageUtils.createRecordMessage(TABLE_NAME, ImmutableMap.of(COLUMN_NAME, COLUMN_VALUE));

    assertEquals(expectedMessage, actualMessage);
  }

  @Test
  public void testCreateRecordMessageWithSingleEntry() {
    final SingerMessage expectedMessage = new SingerMessage()
        .withType(SingerMessage.Type.RECORD)
        .withStream(TABLE_NAME)
        .withRecord(Jsons.jsonNode(ImmutableMap.of(COLUMN_NAME, COLUMN_VALUE)));

    final SingerMessage actualMessage = SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, COLUMN_VALUE);

    assertEquals(expectedMessage, actualMessage);
  }

}
