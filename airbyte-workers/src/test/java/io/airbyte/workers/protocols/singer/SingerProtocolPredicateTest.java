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

package io.airbyte.workers.protocols.singer;

import static org.junit.Assert.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.workers.SingerMessageUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SingerProtocolPredicateTest {

  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  private SingerProtocolPredicate predicate;

  @BeforeEach
  void setup() {
    predicate = new SingerProtocolPredicate();
  }

  @Test
  void testValid() {
    assertTrue(predicate.test(Jsons.jsonNode(SingerMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green"))));
  }

  @Test
  void testInValid() {
    assertFalse(predicate.test(Jsons.deserialize("{ \"fish\": \"tuna\"}")));
  }

  @Test
  void testConcatenatedValid() {
    final String concatenated =
        Jsons.serialize(SingerMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green"))
            + Jsons.serialize(SingerMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow"));
    assertTrue(predicate.test(Jsons.deserialize(concatenated)));
  }

  @Test
  void testMissingNewLineAndLineStartsWithValidRecord() {
    final String concatenated =
        Jsons.serialize(SingerMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green"))
            + "{ \"fish\": \"tuna\"}";
    assertTrue(predicate.test(Jsons.deserialize(concatenated)));
  }

  @Test
  void testMissingNewLineAndLineStartsWithInvalidRecord() {
    final String concatenated =
        "{ \"fish\": \"tuna\"}"
            + Jsons.serialize(SingerMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green"));
    assertFalse(predicate.test(Jsons.deserialize(concatenated)));
  }

}
