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
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class JsonsTest {

  private static final String SERIALIZED_JSON = "{\"str\":\"abc\",\"num\":999,\"numLong\":888}";
  private static final String SERIALIZED_JSON2 = "{\"str\":\"abc\"}";
  private static final String ABC = "abc";
  private static final String DEF = "def";
  private static final String GHI = "ghi";
  private static final String JKL = "jkl";
  private static final String MNO = "mno";
  private static final String PQR = "pqr";
  private static final String STU = "stu";
  private static final String TEST = "test";
  private static final String TEST2 = "test2";
  private static final String XYZ = "xyz";

  @Test
  void testSerialize() {
    assertEquals(
        SERIALIZED_JSON,
        Jsons.serialize(new ToClass(ABC, 999, 888L)));

    assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.serialize(
            ImmutableMap.of(
                TEST, ABC,
                TEST2, DEF)));
  }

  @Test
  void testSerializeJsonNode() {
    assertEquals(
        SERIALIZED_JSON,
        Jsons.serialize(Jsons.jsonNode(new ToClass(ABC, 999, 888L))));

    assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.serialize(Jsons.jsonNode(ImmutableMap.of(
            TEST, ABC,
            TEST2, DEF))));
    // issue: 5878 add test for binary node serialization, binary data are
    // serialized into base64
    assertEquals(
        "{\"test\":\"dGVzdA==\"}",
        Jsons.serialize(Jsons.jsonNode(ImmutableMap.of(
            TEST, new BinaryNode("test".getBytes(StandardCharsets.UTF_8))))));
  }

  @Test
  void testDeserialize() {
    assertEquals(
        new ToClass(ABC, 999, 888L),
        Jsons.deserialize("{\"str\":\"abc\", \"num\": 999, \"numLong\": 888}", ToClass.class));
  }

  @Test
  void testDeserializeToJsonNode() {
    assertEquals(
        SERIALIZED_JSON2,
        Jsons.deserialize(SERIALIZED_JSON2).toString());

    assertEquals(
        "[{\"str\":\"abc\"},{\"str\":\"abc\"}]",
        Jsons.deserialize("[{\"str\":\"abc\"},{\"str\":\"abc\"}]").toString());
    // issue: 5878 add test for binary node deserialization, for now should be
    // base64 string
    assertEquals(
        "{\"test\":\"dGVzdA==\"}",
        Jsons.deserialize("{\"test\":\"dGVzdA==\"}").toString());
  }

  @Test
  void testTryDeserialize() {
    assertEquals(
        Optional.of(new ToClass(ABC, 999, 888L)),
        Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"numLong\": 888}", ToClass.class));

    assertEquals(
        Optional.of(new ToClass(ABC, 999, 0L)),
        Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"test\": 888}", ToClass.class));
  }

  @Test
  void testTryDeserializeToJsonNode() {
    assertEquals(
        Optional.of(Jsons.deserialize(SERIALIZED_JSON2)),
        Jsons.tryDeserialize(SERIALIZED_JSON2));

    assertEquals(
        Optional.empty(),
        Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"test}"));
  }

  @Test
  void testToJsonNode() {
    assertEquals(
        SERIALIZED_JSON,
        Jsons.jsonNode(new ToClass(ABC, 999, 888L)).toString());

    assertEquals(
        "{\"test\":\"abc\",\"test2\":\"def\"}",
        Jsons.jsonNode(
            ImmutableMap.of(
                TEST, ABC,
                TEST2, DEF))
            .toString());

    assertEquals(
        "{\"test\":\"abc\",\"test2\":{\"inner\":1}}",
        Jsons.jsonNode(
            ImmutableMap.of(
                TEST, ABC,
                TEST2, ImmutableMap.of("inner", 1)))
            .toString());

    assertEquals(
        Jsons.jsonNode(new ToClass(ABC, 999, 888L)),
        Jsons.jsonNode(Jsons.jsonNode(new ToClass(ABC, 999, 888L))));
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
    final ToClass expected = new ToClass(ABC, 999, 888L);
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
    final ToClass expected = new ToClass(ABC, 999, 888L);
    assertEquals(
        Optional.of(expected),
        Jsons.tryObject(Jsons.deserialize(SERIALIZED_JSON), ToClass.class));

    assertEquals(
        Optional.of(expected),
        Jsons.tryObject(Jsons.deserialize(SERIALIZED_JSON), new TypeReference<ToClass>() {}));

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
    final JsonNode jsonNode = Jsons.jsonNode(ImmutableMap.of(TEST, ABC, TEST2, DEF));
    assertEquals(Sets.newHashSet(TEST, TEST2), Jsons.keys(jsonNode));

    // test literal jsonNode
    assertEquals(Collections.emptySet(), Jsons.keys(jsonNode.get("test")));

    // test nested object json node. should only return top-level keys.
    final JsonNode nestedJsonNode = Jsons.jsonNode(ImmutableMap.of(TEST, ABC, TEST2, ImmutableMap.of("test3", "def")));
    assertEquals(Sets.newHashSet(TEST, TEST2), Jsons.keys(nestedJsonNode));

    // test array json node
    final JsonNode arrayJsonNode = Jsons.jsonNode(ImmutableList.of(ImmutableMap.of(TEST, ABC, TEST2, DEF)));
    assertEquals(Collections.emptySet(), Jsons.keys(arrayJsonNode));
  }

  @Test
  void testToPrettyString() {
    final JsonNode jsonNode = Jsons.jsonNode(ImmutableMap.of(TEST, ABC));
    final String expectedOutput = ""
        + "{\n"
        + "  \"test\": \"abc\"\n"
        + "}\n";
    assertEquals(expectedOutput, Jsons.toPrettyString(jsonNode));
  }

  @Test
  void testGetOptional() {
    final JsonNode json = Jsons
        .deserialize("{ \"abc\": { \"def\": \"ghi\" }, \"jkl\": {}, \"mno\": \"pqr\", \"stu\": null }");

    assertEquals(Optional.of(Jsons.jsonNode(GHI)), Jsons.getOptional(json, ABC, DEF));
    assertEquals(Optional.of(Jsons.emptyObject()), Jsons.getOptional(json, JKL));
    assertEquals(Optional.of(Jsons.jsonNode(PQR)), Jsons.getOptional(json, MNO));
    assertEquals(Optional.of(Jsons.jsonNode(null)), Jsons.getOptional(json, STU));
    assertEquals(Optional.empty(), Jsons.getOptional(json, XYZ));
    assertEquals(Optional.empty(), Jsons.getOptional(json, ABC, XYZ));
    assertEquals(Optional.empty(), Jsons.getOptional(json, ABC, DEF, XYZ));
    assertEquals(Optional.empty(), Jsons.getOptional(json, ABC, JKL, XYZ));
    assertEquals(Optional.empty(), Jsons.getOptional(json, STU, XYZ));
  }

  @Test
  void testGetStringOrNull() {
    final JsonNode json = Jsons.deserialize("{ \"abc\": { \"def\": \"ghi\" }, \"jkl\": \"mno\", \"pqr\": 1 }");

    assertEquals(GHI, Jsons.getStringOrNull(json, ABC, DEF));
    assertEquals(MNO, Jsons.getStringOrNull(json, JKL));
    assertEquals("1", Jsons.getStringOrNull(json, PQR));
    assertNull(Jsons.getStringOrNull(json, ABC, DEF, XYZ));
    assertNull(Jsons.getStringOrNull(json, XYZ));
  }

  @Test
  void testGetEstimatedByteSize() {
    final JsonNode json = Jsons.deserialize("{\"string_key\":\"abc\",\"array_key\":[\"item1\", \"item2\"]}");
    assertEquals(Jsons.toBytes(json).length, Jsons.getEstimatedByteSize(json));
  }

  @Test
  void testFlatten__noArrays() {
    final JsonNode json = Jsons.deserialize("{ \"abc\": { \"def\": \"ghi\" }, \"jkl\": true, \"pqr\": 1 }");
    Map<String, Object> expected = Stream.of(new Object[][] {
      {"abc.def", GHI},
      {JKL, true},
      {PQR, 1},
    }).collect(Collectors.toMap(data -> (String) data[0], data -> data[1]));
    assertEquals(expected, Jsons.flatten(json, false));
  }

  @Test
  void testFlatten__withArraysNoApplyFlatten() {
    final JsonNode json = Jsons
        .deserialize("{ \"abc\": [{ \"def\": \"ghi\" }, { \"fed\": \"ihg\" }], \"jkl\": true, \"pqr\": 1 }");
    Map<String, Object> expected = Stream.of(new Object[][] {
      {ABC, "[{\"def\":\"ghi\"},{\"fed\":\"ihg\"}]"},
      {JKL, true},
      {PQR, 1},
    }).collect(Collectors.toMap(data -> (String) data[0], data -> data[1]));
    assertEquals(expected, Jsons.flatten(json, false));
  }

  @Test
  void testFlatten__checkBackwardCompatiblity() {
    final JsonNode json = Jsons
        .deserialize("{ \"abc\": [{ \"def\": \"ghi\" }, { \"fed\": \"ihg\" }], \"jkl\": true, \"pqr\": 1 }");
    Map<String, Object> expected = Stream.of(new Object[][] {
      {ABC, "[{\"def\":\"ghi\"},{\"fed\":\"ihg\"}]"},
      {JKL, true},
      {PQR, 1},
    }).collect(Collectors.toMap(data -> (String) data[0], data -> data[1]));
    assertEquals(expected, Jsons.flatten(json));
  }

  @Test
  void testFlatten__withArraysApplyFlatten() {
    final JsonNode json = Jsons
        .deserialize("{ \"abc\": [{ \"def\": \"ghi\" }, { \"fed\": \"ihg\" }], \"jkl\": true, \"pqr\": 1 }");
    Map<String, Object> expected = Stream.of(new Object[][] {
      {"abc.[0].def", "ghi"},
      {"abc.[1].fed", "ihg"},
      {JKL, true},
      {PQR, 1},
    }).collect(Collectors.toMap(data -> (String) data[0], data -> data[1]));
    assertEquals(expected, Jsons.flatten(json, true));
  }

  @Test
  void testFlatten__withArraysApplyFlattenNested() {
    final JsonNode json = Jsons
        .deserialize(
            "{ \"abc\": [{ \"def\": {\"ghi\": [\"xyz\"] }}, { \"fed\": \"ihg\" }], \"jkl\": true, \"pqr\": 1 }");
    Map<String, Object> expected = Stream.of(new Object[][] {
      {"abc.[0].def.ghi.[0]", "xyz"},
      {"abc.[1].fed", "ihg"},
      {JKL, true},
      {PQR, 1},
    }).collect(Collectors.toMap(data -> (String) data[0], data -> data[1]));
    assertEquals(expected, Jsons.flatten(json, true));
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
