package io.dataline.workers.protocols.singer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.dataline.commons.json.Jsons;
import org.junit.jupiter.api.Test;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

class JsonNodeIteratorTest {

  private static final List<JsonNode> EXPECTED = Lists.newArrayList(
      Jsons.deserialize("{ \"a\": \"a\"}"),
      Jsons.deserialize("{ \"a\": \"b\"}"),
      Jsons.deserialize("{ \"a\": \"c\"}"));

  @Test
  void testNewLineDelimitedJsonStream() throws IOException {
    assertEquals(EXPECTED, run("{ \"a\": \"a\"}\n{ \"a\": \"b\"}\n{ \"a\": \"c\"}"));
  }

  @Test
  void testNoDelimiterJsonStream() throws IOException {
    assertEquals(EXPECTED, run("{ \"a\": \"a\"}{ \"a\": \"b\"}\n{ \"a\": \"c\"}"));
  }

  @Test
  void testNewLineDelimitedJsonStreamWithExtraNewLines() throws IOException {
    assertEquals(EXPECTED, run("{ \"a\":\n \"a\"}\n{\n \"a\":\n \"b\"\n}\n{ \"a\": \"c\"}"));
  }

  @Test
  void testInputStreamWithNonJsonLines() throws IOException {
    assertEquals(EXPECTED, run("{ \"a\": \"a\"}\nHe's dead, Jim!\n{ \"a\": \"b\"}\nResistance is futile.\n{ \"a\": \"c\"}"));
  }

  @Test
  void testCommaDelimitedJsonStream() throws IOException {
    assertEquals(EXPECTED, run("{ \"a\": \"a\"},{ \"a\": \"b\"},{ \"a\": \"c\"}"));
  }

  private static List<JsonNode> run(String testString) throws IOException {
    final InputStream targetStream = new ByteArrayInputStream(testString.getBytes());
    return Lists.newArrayList(new JsonNodeIterator(targetStream));
  }

}
