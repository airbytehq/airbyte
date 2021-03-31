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

package io.airbyte.db;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.ImmutableMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class PgLsnTest {

  private static final Map<String, Long> TEST_LSNS = ImmutableMap.<String, Long>builder()
      .put("0/15E7A10", 22968848L)
      .put("0/15E7B08", 22969096L)
      .put("16/15E7B08", 94512249608L)
      .put("16/FFFFFFFF", 98784247807L)
      .put("7FFFFFFF/FFFFFFFF", Long.MAX_VALUE)
      .put("0/0", 0L)
      .build();

  @Test
  void testLsnToLong() {
    TEST_LSNS.forEach(
        (key, value) -> assertEquals(value, PgLsn.lsnToLong(key), String.format("Conversion failed. lsn: %s long value: %s", key, value)));
  }

  @Test
  void testLongToLsn() {
    TEST_LSNS.forEach(
        (key, value) -> assertEquals(key, PgLsn.longToLsn(value), String.format("Conversion failed. lsn: %s long value: %s", key, value)));
  }

}
