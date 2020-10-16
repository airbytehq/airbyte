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

package io.airbyte.commons.json;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class JsonsTest {

  @Test
  void testSerialize() {
    Assertions.assertEquals(
        "{\"str\":\"abc\",\"num\":999,\"numLong\":888}",
        Jsons.serialize(new ToClass("abc", 999, 888L)));

    Assertions.assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.serialize(
            ImmutableMap.of(
                "test", "abc",
                "test2", "def")));
  }

  @Test
  void testSerializeJsonNode() {
    Assertions.assertEquals(
        "{\"str\":\"abc\",\"num\":999,\"numLong\":888}",
        Jsons.serialize(Jsons.jsonNode(new ToClass("abc", 999, 888L))));

    Assertions.assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.serialize(Jsons.jsonNode(ImmutableMap.of(
            "test", "abc",
            "test2", "def"))));
  }

  @Test
  void testDeserialize() {
    Assertions.assertEquals(
        new ToClass("abc", 999, 888L),
        Jsons.deserialize("{\"str\":\"abc\", \"num\": 999, \"numLong\": 888}", ToClass.class));
  }

  @Test
  void testDeserializeToJsonNode() {
    Assertions.assertEquals(
        "{\"str\":\"abc\"}",
        Jsons.deserialize("{\"str\":\"abc\"}").toString());

    Assertions.assertEquals(
        "[{\"str\":\"abc\"},{\"str\":\"abc\"}]",
        Jsons.deserialize("[{\"str\":\"abc\"},{\"str\":\"abc\"}]").toString());
  }

  @Test
  void testTryDeserialize() {
    Assertions.assertEquals(
        Optional.of(new ToClass("abc", 999, 888L)),
        Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"numLong\": 888}", ToClass.class));

    Assertions.assertEquals(
        Optional.empty(),
        Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"test\": 888}", ToClass.class));
  }

  @Test
  void testTryDeserializeToJsonNode() {
    Assertions.assertEquals(
        Optional.of(Jsons.deserialize("{\"str\":\"abc\"}")),
        Jsons.tryDeserialize("{\"str\":\"abc\"}"));

    Assertions.assertEquals(
        Optional.empty(),
        Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"test}"));
  }

  @Test
  void testToJsonNode() {
    Assertions.assertEquals(
        "{\"str\":\"abc\",\"num\":999,\"numLong\":888}",
        Jsons.jsonNode(new ToClass("abc", 999, 888L)).toString());

    Assertions.assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.jsonNode(
            ImmutableMap.of(
                "test", "abc",
                "test2", "def"))
            .toString());

    Assertions.assertEquals(
        "{\"test\":\"abc\",\"test2\":{\"inner\":1}}",
        Jsons.jsonNode(
            ImmutableMap.of(
                "test", "abc",
                "test2", ImmutableMap.of("inner", 1)))
            .toString());

    Assertions.assertEquals(
        Jsons.jsonNode(new ToClass("abc", 999, 888L)),
        Jsons.jsonNode(Jsons.jsonNode(new ToClass("abc", 999, 888L))));
  }

  @Test
  void testToObject() {
    final ToClass expected = new ToClass("abc", 999, 888L);
    Assertions.assertEquals(
        expected,
        Jsons.object(Jsons.jsonNode(expected), ToClass.class));

    Assertions.assertEquals(
        Lists.newArrayList(expected),
        Jsons.object(Jsons.jsonNode(Lists.newArrayList(expected)), new TypeReference<List<ToClass>>() {}));

    Assertions.assertThrows(IllegalArgumentException.class,
        () -> Jsons.object(Jsons.deserialize("{\"a\":1}"), ToClass.class));
  }

  @Test
  void testTryToObject() {
    final ToClass expected = new ToClass("abc", 999, 888L);
    Assertions.assertEquals(
        Optional.of(expected),
        Jsons.tryObject(Jsons.deserialize("{\"str\":\"abc\",\"num\":999,\"numLong\":888}"), ToClass.class));

    Assertions.assertEquals(
        Optional.of(expected),
        Jsons.tryObject(Jsons.deserialize("{\"str\":\"abc\",\"num\":999,\"numLong\":888}"), new TypeReference<ToClass>() {}));

    Assertions.assertEquals(
        Optional.empty(),
        Jsons.tryObject(Jsons.deserialize("{\"str1\":\"abc\"}"), ToClass.class));

    Assertions.assertEquals(
        Optional.empty(),
        Jsons.tryObject(Jsons.deserialize("{\"str1\":\"abc\"}"), new TypeReference<ToClass>() {}));

  }

  @Test
  void testClone() {
    final ToClass expected = new ToClass("abc", 999, 888L);
    final ToClass actual = Jsons.clone(expected);
    Assertions.assertNotSame(expected, actual);
    Assertions.assertEquals(expected, actual);
  }

  @Test
  void testMutateTypeToArrayStandard() {
    final JsonNode expectedWithoutType = Jsons.deserialize("{\"test\":\"abc\"}");
    final JsonNode actualWithoutType = Jsons.clone(expectedWithoutType);
    JsonSchemas.mutateTypeToArrayStandard(expectedWithoutType);
    Assertions.assertEquals(expectedWithoutType, actualWithoutType);

    final JsonNode expectedWithArrayType = Jsons.deserialize("{\"test\":\"abc\", \"type\":[\"object\"]}");
    final JsonNode actualWithArrayType = Jsons.clone(expectedWithArrayType);
    JsonSchemas.mutateTypeToArrayStandard(actualWithArrayType);
    Assertions.assertEquals(expectedWithoutType, actualWithoutType);

    final JsonNode expectedWithoutArrayType = Jsons.deserialize("{\"test\":\"abc\", \"type\":[\"object\"]}");
    final JsonNode actualWithStringType = Jsons.deserialize("{\"test\":\"abc\", \"type\":\"object\"}");
    JsonSchemas.mutateTypeToArrayStandard(actualWithStringType);
    Assertions.assertEquals(expectedWithoutArrayType, actualWithStringType);
  }

  @Test
  void testToBytes() {
    final String jsonString = "{\"test\":\"abc\",\"type\":[\"object\"]}";
    Assertions.assertArrayEquals(jsonString.getBytes(Charsets.UTF_8), Jsons.toBytes(Jsons.deserialize(jsonString)));
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
