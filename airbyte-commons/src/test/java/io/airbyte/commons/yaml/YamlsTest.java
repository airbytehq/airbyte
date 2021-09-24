/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.yaml;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableConsumer;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.util.AutoCloseableIterator;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
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

  @Test
  void testStreamRead() throws IOException {
    List<ToClass> classes = Lists.newArrayList(
        new ToClass("1", 1, 1),
        new ToClass("2", 2, 2),
        new ToClass("3", 3, 3));
    ByteArrayInputStream input = spy(new ByteArrayInputStream(Yamls.serialize(classes).getBytes(StandardCharsets.UTF_8)));

    try (AutoCloseableIterator<JsonNode> iterator = Yamls.deserializeArray(input)) {
      assertEquals(
          classes,
          MoreStreams.toStream(iterator)
              .map(e -> Jsons.object(e, ToClass.class))
              .collect(Collectors.toList()));
    } catch (Exception e) {
      fail();
    }

    verify(input).close();
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
