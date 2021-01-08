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

package io.airbyte.commons.yaml;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableConsumer;
import java.io.StringWriter;
import java.util.List;
import java.util.Objects;
import org.junit.jupiter.api.Test;

class YamlsTest {

  @Test
  void testSerialize() {
    assertEquals(
        "---\n"
            + "str: \"abc\"\n"
            + "num: 999\n"
            + "numLong: 888\n",
        Yamls.serialize(new ToClass("abc", 999, 888L)));

    assertEquals(
        "---\n"
            + "test: \"abc\"\n"
            + "test2: \"def\"\n",
        Yamls.serialize(
            ImmutableMap.of(
                "test", "abc",
                "test2", "def")));
  }

  @Test
  void testSerializeJsonNode() {
    assertEquals(
        "---\n"
            + "str: \"abc\"\n"
            + "num: 999\n"
            + "numLong: 888\n",
        Yamls.serialize(Jsons.jsonNode(new ToClass("abc", 999, 888L))));

    assertEquals(
        "---\n"
            + "test: \"abc\"\n"
            + "test2: \"def\"\n",
        Yamls.serialize(Jsons.jsonNode(ImmutableMap.of(
            "test", "abc",
            "test2", "def"))));
  }

  @Test
  void testDeserialize() {
    assertEquals(
        new ToClass("abc", 999, 888L),
        Yamls.deserialize(
            "---\n"
                + "str: \"abc\"\n"
                + "num: \"999\"\n"
                + "numLong: \"888\"\n",
            ToClass.class));
  }

  @Test
  void testDeserializeToJsonNode() {
    assertEquals(
        "{\"str\":\"abc\"}",
        Yamls.deserialize(
            "---\n"
                + "str: \"abc\"\n")
            .toString());

    assertEquals(
        "[{\"str\":\"abc\"},{\"str\":\"abc\"}]",
        Yamls.deserialize(
            "---\n"
                + "- str: \"abc\"\n"
                + "- str: \"abc\"\n")
            .toString());
  }

  @Test
  void testListWriter() throws Exception {
    final List<Integer> values = Lists.newArrayList(1, 2, 3);
    final StringWriter writer = spy(new StringWriter());
    final CloseableConsumer<Integer> consumer = Yamls.listWriter(writer);
    values.forEach(consumer);
    consumer.close();

    verify(writer).close();

    final List<?> deserialize = Yamls.deserialize(writer.toString(), List.class);
    assertEquals(values, deserialize);
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
