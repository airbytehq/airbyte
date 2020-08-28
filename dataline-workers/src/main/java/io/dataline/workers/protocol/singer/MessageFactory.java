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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.dataline.config.SingerMessage;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.Optional;

public class MessageFactory {

  private static final DateTimeFormatter SINGER_DATETIME_FORMATTER =
      DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'").withZone(ZoneId.of("UTC"));

  public static SingerMessage createRecordMessage(
      String tableName, JsonNode record, Instant timeExtracted) {

    final String recordJson;
    try {
      recordJson = new ObjectMapper().writeValueAsString(record);
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }

    final SingerMessage singerMessage = new SingerMessage();
    singerMessage.setType(SingerMessage.Type.RECORD);
    singerMessage.setRecord(recordJson);
    singerMessage.setStream(tableName);

    Optional.ofNullable(timeExtracted)
        .ifPresent(
            instant -> singerMessage.setTimeExtracted(SINGER_DATETIME_FORMATTER.format(instant)));

    return singerMessage;
  }

  public static SingerMessage createRecordMessage(String tableName, JsonNode record) {
    return createRecordMessage(tableName, record, null);
  }

  public static SingerMessage createRecordMessage(String tableName, Map<String, String> record) {
    final ObjectMapper objectMapper = new ObjectMapper();
    String json = null;
    try {
      json = objectMapper.writeValueAsString(record);
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }

    return createRecordMessage(tableName, json, null);
  }

  public static SingerMessage createRecordMessage(String tableName, String key, String value) {
    final ObjectMapper objectMapper = new ObjectMapper();
    final ObjectNode record = objectMapper.createObjectNode();
    record.put(key, value);

    return createRecordMessage(tableName, record);
  }
}
