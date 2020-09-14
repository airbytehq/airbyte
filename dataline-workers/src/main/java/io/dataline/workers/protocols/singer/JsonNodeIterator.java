package io.dataline.workers.protocols.singer;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.AbstractIterator;
import java.io.IOException;
import java.io.InputStream;

/**
 * Iterator to consume input stream from a SingerTap. Rules:
 * 1. JSON objects should be new line delimited.
 * 2. Some lines will not be JSON and should be ignored.
 * 3. No guarantee that there are not new lines within a JSON object.
 */
public class JsonNodeIterator extends AbstractIterator<JsonNode> {

  private final JsonParser parser;
  private final ObjectMapper objectMapper;

  public JsonNodeIterator(InputStream is) throws IOException {
    parser = new JsonFactory().createParser(is);
    objectMapper = new ObjectMapper();
  }

  @Override
  protected JsonNode computeNext() {
    while (true) {
      try {
        final JsonNode treeNode = objectMapper.readTree(parser);
        if (treeNode == null) {
          return endOfData();
        } else {
          return treeNode;
        }
        // When no object can be parsed, the mapper throws a JsonParseException. This is our cue to move on to the
        // next token. This could be come a performance problem because it means for each word it finds, it throws
        // an exception.
      } catch (JsonParseException e) {
        // no op.
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    }
  }
}
