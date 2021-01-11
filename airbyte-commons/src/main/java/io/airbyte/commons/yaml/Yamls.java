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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SequenceWriter;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import io.airbyte.commons.lang.CloseableConsumer;
import io.airbyte.commons.lang.Exceptions;
import java.io.IOException;
import java.io.Writer;

public class Yamls {

  // Object Mapper is thread-safe
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper(new YAMLFactory());

  public static <T> String serialize(T object) {
    try {
      return OBJECT_MAPPER.writeValueAsString(object);
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

  public static <T> T deserialize(final String jsonString, final Class<T> klass) {
    try {
      return OBJECT_MAPPER.readValue(jsonString, klass);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static JsonNode deserialize(final String jsonString) {
    try {
      return OBJECT_MAPPER.readTree(jsonString);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  // todo (cgardens) - share this with Jsons if ever needed.

  /**
   * Creates a consumer that writes list items to the writer in a streaming fashion.
   *
   * @param writer writer to write to
   * @param <T> type of items being written
   * @return consumer that is able to write element to a list element by element. must be closed!
   */
  public static <T> CloseableConsumer<T> listWriter(Writer writer) {
    return new YamlConsumer<>(writer, OBJECT_MAPPER);
  }

  public static class YamlConsumer<T> implements CloseableConsumer<T> {

    private final SequenceWriter sequenceWriter;

    public YamlConsumer(Writer writer, ObjectMapper objectMapper) {
      this.sequenceWriter = Exceptions.toRuntime(() -> objectMapper.writer().writeValuesAsArray(writer));

    }

    @Override
    public void accept(T t) {
      try {
        sequenceWriter.write(t);
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    }

    @Override
    public void close() throws Exception {
      // closing the SequenceWriter closes the Writer that it wraps.
      sequenceWriter.close();
    }

  }

}
