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
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.dataline.commons.json.Jsons;
import io.dataline.singer.SingerMessage;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.Optional;

public class MessageUtils {

  @VisibleForTesting
  static final DateTimeFormatter SINGER_DATETIME_FORMATTER =
      DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'").withZone(ZoneId.of("UTC"));

  public static SingerMessage createRecordMessage(String tableName,
                                                  JsonNode record,
                                                  Instant timeExtracted) {
    final SingerMessage singerMessage = new SingerMessage();
    singerMessage.withType(SingerMessage.Type.RECORD);
    singerMessage.withRecord(record);
    singerMessage.withStream(tableName);

    Optional.ofNullable(timeExtracted)
        .ifPresent(
            instant -> singerMessage.withTimeExtracted(SINGER_DATETIME_FORMATTER.format(instant)));

    return singerMessage;
  }

  public static SingerMessage createRecordMessage(String tableName, String key, String value) {
    return createRecordMessage(tableName, ImmutableMap.of(key, value));
  }

  public static SingerMessage createRecordMessage(String tableName, Map<String, String> record) {
    return createRecordMessage(tableName, Jsons.jsonNode(record), null);
  }

}
