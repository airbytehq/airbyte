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

package io.dataline.commons.json;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.collect.ImmutableMap;
import java.util.Objects;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class JsonsTest {

  @Test
  void testToJson() {
    Assertions.assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.toJson(
            ImmutableMap.of(
                "test", "abc",
                "test2", "def")));
  }

  @Test
  void testToClass() {
    Assertions.assertEquals(
        new ToClass("abc", 999, 888L),
        Jsons.toClass("{\"str\":\"abc\", \"num\": 999, \"numLong\": 888}", ToClass.class));
  }

  @Test
  void testToJsonNode() {
    Assertions.assertEquals("{\"str\":\"abc\"}", Jsons.toJsonNode("{\"str\":\"abc\"}").toString());

    Assertions.assertEquals(
        "[{\"str\":\"abc\"},{\"str\":\"abc\"}]",
        Jsons.toJsonNode("[{\"str\":\"abc\"},{\"str\":\"abc\"}]").toString());
  }

  private static class ToClass {

    @JsonProperty("str")
    String str;

    @JsonProperty("num")
    Integer num;

    @JsonProperty("numLong")
    long numLong;

    public ToClass() {}

    public ToClass(String str, Integer num, long numLong) {
      this.str = str;
      this.num = num;
      this.numLong = numLong;
    }

    @Override
    public boolean equals(Object o) {
      if (this == o) {
        return true;
      }
      if (o == null || getClass() != o.getClass()) {
        return false;
      }
      ToClass toClass = (ToClass) o;
      return numLong == toClass.numLong
          && Objects.equals(str, toClass.str)
          && Objects.equals(num, toClass.num);
    }

    @Override
    public int hashCode() {
      return Objects.hash(str, num, numLong);
    }
  }
}
