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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.dataline.commons.json.Jsons;
import io.dataline.singer.SingerMessage;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Collections;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;

class DefaultSingerStreamFactoryTest {

  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";

  private SingerProtocolPredicate singerProtocolPredicate;
  private Logger logger;

  @BeforeEach
  public void setup() {
    singerProtocolPredicate = mock(SingerProtocolPredicate.class);
    when(singerProtocolPredicate.test(any())).thenReturn(true);
    logger = mock(Logger.class);
  }

  @Test
  public void testValid() {
    final SingerMessage record1 = SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "green");

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(Jsons.serialize(record1));
    final Stream<SingerMessage> expectedStream = Stream.of(record1);

    assertEquals(expectedStream.collect(Collectors.toList()), messageStream.collect(Collectors.toList()));
    verifyNoInteractions(logger);
  }

  @Test
  public void testLoggingLine() {
    final String invalidRecord = "invalid line";

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(invalidRecord);

    assertEquals(Collections.emptyList(), messageStream.collect(Collectors.toList()));
    verify(logger).info(anyString());
    verifyNoMoreInteractions(logger);
  }

  @Test
  public void testFailValidation() {
    final String invalidRecord = "{ \"fish\": \"tuna\"}";

    when(singerProtocolPredicate.test(Jsons.deserialize(invalidRecord))).thenReturn(false);

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(invalidRecord);

    assertEquals(Collections.emptyList(), messageStream.collect(Collectors.toList()));
    verify(logger).error(anyString(), anyString());
    verifyNoMoreInteractions(logger);
  }

  @Test
  public void testFailDeserialization() {
    final String invalidRecord = "{ \"type\": \"abc\"}";

    when(singerProtocolPredicate.test(Jsons.deserialize(invalidRecord))).thenReturn(true);

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(invalidRecord);

    assertEquals(Collections.emptyList(), messageStream.collect(Collectors.toList()));
    verify(logger).error(anyString(), anyString());
    verifyNoMoreInteractions(logger);
  }

  @Test
  @Disabled
  public void testMissingNewLineBetweenValidRecords() {
    final SingerMessage record1 = SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "green");
    final SingerMessage record2 = SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final String inputString = Jsons.serialize(record1) + Jsons.serialize(record2);

    final Stream<SingerMessage> messageStream = stringToSingerMessageStream(inputString);

    assertEquals(Collections.emptyList(), messageStream.collect(Collectors.toList()));
    verify(logger).error(anyString(), anyString());
    verifyNoMoreInteractions(logger);
  }

  private Stream<SingerMessage> stringToSingerMessageStream(String inputString) {
    InputStream inputStream = new ByteArrayInputStream(inputString.getBytes());
    final BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
    return new DefaultSingerStreamFactory(singerProtocolPredicate, logger).create(bufferedReader);
  }

}
