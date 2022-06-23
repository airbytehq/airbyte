/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.json;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.BinaryNode;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class JsonsTest {

  @Test
  void testSerialize() {
    assertEquals(
        "{\"str\":\"abc\",\"num\":999,\"numLong\":888}",
        Jsons.serialize(new ToClass("abc", 999, 888L)));

    assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.serialize(
            ImmutableMap.of(
                "test", "abc",
                "test2", "def")));
  }

  @Test
  void testSerializeJsonNode() {
    assertEquals(
        "{\"str\":\"abc\",\"num\":999,\"numLong\":888}",
        Jsons.serialize(Jsons.jsonNode(new ToClass("abc", 999, 888L))));

    assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.serialize(Jsons.jsonNode(ImmutableMap.of(
            "test", "abc",
            "test2", "def"))));
    // issue: 5878 add test for binary node serialization, binary data are serialized into base64
    assertEquals(
        "{\"test\":\"dGVzdA==\"}",
        Jsons.serialize(Jsons.jsonNode(ImmutableMap.of(
            "test", new BinaryNode("test".getBytes(StandardCharsets.UTF_8))))));
  }

  @Test
  void testDeserialize() {
    assertEquals(
        new ToClass("abc", 999, 888L),
        Jsons.deserialize("{\"str\":\"abc\", \"num\": 999, \"numLong\": 888}", ToClass.class));
  }

  @Test
  void testDeserializeToJsonNode() {
    assertEquals(
        "{\"str\":\"abc\"}",
        Jsons.deserialize("{\"str\":\"abc\"}").toString());

    assertEquals(
        "[{\"str\":\"abc\"},{\"str\":\"abc\"}]",
        Jsons.deserialize("[{\"str\":\"abc\"},{\"str\":\"abc\"}]").toString());
    // issue: 5878 add test for binary node deserialization, for now should be base64 string
    assertEquals(
        "{\"test\":\"dGVzdA==\"}",
        Jsons.deserialize("{\"test\":\"dGVzdA==\"}").toString());
  }

  @Test
  void testTryDeserialize() {
    assertEquals(
        Optional.of(new ToClass("abc", 999, 888L)),
        Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"numLong\": 888}", ToClass.class));

    assertEquals(
        Optional.of(new ToClass("abc", 999, 0L)),
        Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"test\": 888}", ToClass.class));
  }

  @Test
  void testTryDeserializeToJsonNode() {
    assertEquals(
        Optional.of(Jsons.deserialize("{\"str\":\"abc\"}")),
        Jsons.tryDeserialize("{\"str\":\"abc\"}"));

    assertEquals(
        Optional.empty(),
        Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"test}"));
  }

  @Test
  void testToJsonNode() {
    assertEquals(
        "{\"str\":\"abc\",\"num\":999,\"numLong\":888}",
        Jsons.jsonNode(new ToClass("abc", 999, 888L)).toString());

    assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.jsonNode(
            ImmutableMap.of(
                "test", "abc",
                "test2", "def"))
            .toString());

    assertEquals(
        "{\"test\":\"abc\",\"test2\":{\"inner\":1}}",
        Jsons.jsonNode(
            ImmutableMap.of(
                "test", "abc",
                "test2", ImmutableMap.of("inner", 1)))
            .toString());

    assertEquals(
        Jsons.jsonNode(new ToClass("abc", 999, 888L)),
        Jsons.jsonNode(Jsons.jsonNode(new ToClass("abc", 999, 888L))));
  }

  @Test
  void testEmptyObject() {
    assertEquals(Jsons.deserialize("{}"), Jsons.emptyObject());
  }

  @Test
  void testArrayNode() {
    assertEquals(Jsons.deserialize("[]"), Jsons.arrayNode());
  }

  @Test
  void testToObject() {
    final ToClass expected = new ToClass("abc", 999, 888L);
    assertEquals(
        expected,
        Jsons.object(Jsons.jsonNode(expected), ToClass.class));

    assertEquals(
        Lists.newArrayList(expected),
        Jsons.object(Jsons.jsonNode(Lists.newArrayList(expected)), new TypeReference<List<ToClass>>() {}));

    assertEquals(
        new ToClass(),
        Jsons.object(Jsons.deserialize("{\"a\":1}"), ToClass.class));
  }

  @Test
  void testTryToObject() {
    final ToClass expected = new ToClass("abc", 999, 888L);
    assertEquals(
        Optional.of(expected),
        Jsons.tryObject(Jsons.deserialize("{\"str\":\"abc\",\"num\":999,\"numLong\":888}"), ToClass.class));

    assertEquals(
        Optional.of(expected),
        Jsons.tryObject(Jsons.deserialize("{\"str\":\"abc\",\"num\":999,\"numLong\":888}"), new TypeReference<ToClass>() {}));

    final ToClass emptyExpected = new ToClass();
    assertEquals(
        Optional.of(emptyExpected),
        Jsons.tryObject(Jsons.deserialize("{\"str1\":\"abc\"}"), ToClass.class));

    assertEquals(
        Optional.of(emptyExpected),
        Jsons.tryObject(Jsons.deserialize("{\"str1\":\"abc\"}"), new TypeReference<ToClass>() {}));

  }

  @Test
  void testClone() {
    final ToClass expected = new ToClass("abc", 999, 888L);
    final ToClass actual = Jsons.clone(expected);
    assertNotSame(expected, actual);
    assertEquals(expected, actual);
  }

  @Test
  void testToBytes() {
    final String jsonString = "{\"test\":\"abc\",\"type\":[\"object\"]}";
    assertArrayEquals(jsonString.getBytes(Charsets.UTF_8), Jsons.toBytes(Jsons.deserialize(jsonString)));
  }

  @Test
  void testKeys() {
    // test object json node
    final JsonNode jsonNode = Jsons.jsonNode(ImmutableMap.of("test", "abc", "test2", "def"));
    assertEquals(Sets.newHashSet("test", "test2"), Jsons.keys(jsonNode));

    // test literal jsonNode
    assertEquals(Collections.emptySet(), Jsons.keys(jsonNode.get("test")));

    // test nested object json node. should only return top-level keys.
    final JsonNode nestedJsonNode = Jsons.jsonNode(ImmutableMap.of("test", "abc", "test2", ImmutableMap.of("test3", "def")));
    assertEquals(Sets.newHashSet("test", "test2"), Jsons.keys(nestedJsonNode));

    // test array json node
    final JsonNode arrayJsonNode = Jsons.jsonNode(ImmutableList.of(ImmutableMap.of("test", "abc", "test2", "def")));
    assertEquals(Collections.emptySet(), Jsons.keys(arrayJsonNode));
  }

  @Test
  void testToPrettyString() {
    final JsonNode jsonNode = Jsons.jsonNode(ImmutableMap.of("test", "abc"));
    final String expectedOutput = ""
        + "{\n"
        + "  \"test\": \"abc\"\n"
        + "}\n";
    assertEquals(expectedOutput, Jsons.toPrettyString(jsonNode));
  }

  @Test
  void testGetOptional() {
    final JsonNode json = Jsons.deserialize("{ \"abc\": { \"def\": \"ghi\" }, \"jkl\": {}, \"mno\": \"pqr\", \"stu\": null }");

    assertEquals(Optional.of(Jsons.jsonNode("ghi")), Jsons.getOptional(json, "abc", "def"));
    assertEquals(Optional.of(Jsons.emptyObject()), Jsons.getOptional(json, "jkl"));
    assertEquals(Optional.of(Jsons.jsonNode("pqr")), Jsons.getOptional(json, "mno"));
    assertEquals(Optional.of(Jsons.jsonNode(null)), Jsons.getOptional(json, "stu"));
    assertEquals(Optional.empty(), Jsons.getOptional(json, "xyz"));
    assertEquals(Optional.empty(), Jsons.getOptional(json, "abc", "xyz"));
    assertEquals(Optional.empty(), Jsons.getOptional(json, "abc", "def", "xyz"));
    assertEquals(Optional.empty(), Jsons.getOptional(json, "abc", "jkl", "xyz"));
    assertEquals(Optional.empty(), Jsons.getOptional(json, "stu", "xyz"));
  }

  @Test
  void testGetStringOrNull() {
    final JsonNode json = Jsons.deserialize("{ \"abc\": { \"def\": \"ghi\" }, \"jkl\": \"mno\", \"pqr\": 1 }");

    assertEquals("ghi", Jsons.getStringOrNull(json, "abc", "def"));
    assertEquals("mno", Jsons.getStringOrNull(json, "jkl"));
    assertEquals("1", Jsons.getStringOrNull(json, "pqr"));
    assertNull(Jsons.getStringOrNull(json, "abc", "def", "xyz"));
    assertNull(Jsons.getStringOrNull(json, "xyz"));
  }

  @Test
  void testGetEstimatedByteSize() {
    final JsonNode json = Jsons.deserialize("{\"string_key\":\"abc\",\"array_key\":[\"item1\", \"item2\"]}");
    assertEquals(Jsons.toBytes(json).length, Jsons.getEstimatedByteSize(json));
  }

  private static class ToClass {

    @JsonProperty("str")
    String str;

    @JsonProperty("num")
    Integer num;

    @JsonProperty("numLong")
    long numLong;

    public ToClass() {}

    public ToClass(final String str, final Integer num, final long numLong) {
      this.str = str;
      this.num = num;
      this.numLong = numLong;
    }

    @Override
    public boolean equals(final Object o) {
      if (this == o) {
        return true;
      }
      if (o == null || getClass() != o.getClass()) {
        return false;
      }
      final ToClass toClass = (ToClass) o;
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
