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

package io.dataline.singer;

import com.google.common.collect.Lists;
import io.dataline.commons.json.Jsons;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class SingerTypeDeserializerTest {

  @Test
  void testDeserializationString() {
    Assertions.assertEquals(
        new SingerColumn()
            .withType(Lists.newArrayList(SingerType.STRING)),
        Jsons.deserialize("{\"type\":\"string\"}", SingerColumn.class));
  }

  @Test
  void testDeserializationArray() {
    Assertions.assertEquals(
        new SingerColumn()
            .withType(Lists.newArrayList(SingerType.STRING, SingerType.NULL)),
        Jsons.deserialize("{\"type\":[\"string\",\"null\"]}", SingerColumn.class));
  }

  @Test
  void testBadType() {
    Assertions.assertThrows(RuntimeException.class,
        () -> Jsons.deserialize("{\"type\":1}", SingerColumn.class));
  }

}
