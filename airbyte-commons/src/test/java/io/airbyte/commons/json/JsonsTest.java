/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.json;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.DisplayName;
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
  void testMutateTypeToArrayStandard() {
    final JsonNode expectedWithoutType = Jsons.deserialize("{\"test\":\"abc\"}");
    final JsonNode actualWithoutType = Jsons.clone(expectedWithoutType);
    JsonSchemas.mutateTypeToArrayStandard(expectedWithoutType);
    assertEquals(expectedWithoutType, actualWithoutType);

    final JsonNode expectedWithArrayType = Jsons.deserialize("{\"test\":\"abc\", \"type\":[\"object\"]}");
    final JsonNode actualWithArrayType = Jsons.clone(expectedWithArrayType);
    JsonSchemas.mutateTypeToArrayStandard(actualWithArrayType);
    assertEquals(expectedWithoutType, actualWithoutType);

    final JsonNode expectedWithoutArrayType = Jsons.deserialize("{\"test\":\"abc\", \"type\":[\"object\"]}");
    final JsonNode actualWithStringType = Jsons.deserialize("{\"test\":\"abc\", \"type\":\"object\"}");
    JsonSchemas.mutateTypeToArrayStandard(actualWithStringType);
    assertEquals(expectedWithoutArrayType, actualWithStringType);
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


  private void maskAllValues(final ObjectNode node) {
    for (final String key : Jsons.keys(node)) {
      if (node.get(key).getNodeType() == JsonNodeType.OBJECT) {
        maskAllValues((ObjectNode) node.get(key));
      } else {
        node.set(key, Jsons.getSecretMask());
      }
    }
  }

  @Test
  void testInjectUnnestedNode_Masked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode maskedOauthParams = Jsons.clone(oauthParams);
    maskAllValues(maskedOauthParams);
    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.setAll(maskedOauthParams);

    Jsons.mergeJsons(actual, oauthParams, Jsons.getSecretMask());
    assertEquals(expected, actual);
  }

  @Test
  void testInjectUnnestedNode_Unmasked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());

    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.setAll(oauthParams);

    Jsons.mergeJsons(actual, oauthParams);

    assertEquals(expected, actual);
  }

  @Test
  void testInjectNewNestedNode_Masked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode maskedOauthParams = Jsons.clone(oauthParams);
    maskAllValues(maskedOauthParams);
    final ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("oauth_credentials", oauthParams)
        .build());

    // nested node does not exist in actual object
    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.putObject("oauth_credentials").setAll(maskedOauthParams);

    Jsons.mergeJsons(actual, nestedConfig, Jsons.getSecretMask());
    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("A nested config should be inserted with the same nesting structure")
  void testInjectNewNestedNode_Unmasked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("oauth_credentials", oauthParams)
        .build());

    // nested node does not exist in actual object
    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.putObject("oauth_credentials").setAll(oauthParams);

    Jsons.mergeJsons(actual, nestedConfig);

    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("A nested node which partially exists in the main config should be merged into the main config, not overwrite the whole nested object")
  void testInjectedPartiallyExistingNestedNode_Unmasked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("oauth_credentials", oauthParams)
        .build());

    // nested node partially exists in actual object
    final ObjectNode actual = generateJsonConfig();
    actual.putObject("oauth_credentials").put("irrelevant_field", "_");
    final ObjectNode expected = Jsons.clone(actual);
    ((ObjectNode) expected.get("oauth_credentials")).setAll(oauthParams);

    Jsons.mergeJsons(actual, nestedConfig);

    assertEquals(expected, actual);
  }


  private ObjectNode generateJsonConfig() {
    return (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("apiSecret", "123")
        .put("client", "testing")
        .build());
  }

  private Map<String, String> generateOAuthParameters() {
    return ImmutableMap.<String, String>builder()
        .put("api_secret", "mysecret")
        .put("api_client", UUID.randomUUID().toString())
        .build();
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
