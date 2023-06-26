/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.yaml;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SequenceWriter;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator;
import com.fasterxml.jackson.dataformat.yaml.YAMLParser;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.lang.CloseableConsumer;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import java.io.IOException;
import java.io.InputStream;
import java.io.Writer;
import java.util.Iterator;

@SuppressWarnings("PMD.AvoidBranchingStatementAsLastInLoop")
public class Yamls {

  private static final YAMLFactory YAML_FACTORY = new YAMLFactory();
  private static final ObjectMapper OBJECT_MAPPER = MoreMappers.initYamlMapper(YAML_FACTORY);

  private static final YAMLFactory YAML_FACTORY_WITHOUT_QUOTES = new YAMLFactory().enable(YAMLGenerator.Feature.MINIMIZE_QUOTES);
  private static final ObjectMapper OBJECT_MAPPER_WITHOUT_QUOTES = MoreMappers.initYamlMapper(YAML_FACTORY_WITHOUT_QUOTES);

  /**
   * Serialize object to YAML string. String values WILL be wrapped in double quotes.
   *
   * @param object - object to serialize
   * @return YAML string version of object
   */
  public static <T> String serialize(final T object) {
    try {
      return OBJECT_MAPPER.writeValueAsString(object);
    } catch (final JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Serialize object to YAML string. String values will NOT be wrapped in double quotes.
   *
   * @param object - object to serialize
   * @return YAML string version of object
   */
  public static String serializeWithoutQuotes(final Object object) {
    try {
      return OBJECT_MAPPER_WITHOUT_QUOTES.writeValueAsString(object);
    } catch (final JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

  public static <T> T deserialize(final String yamlString, final Class<T> klass) {
    try {
      return OBJECT_MAPPER.readValue(yamlString, klass);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static <T> T deserialize(final String yamlString, final TypeReference<T> typeReference) {
    try {
      return OBJECT_MAPPER.readValue(yamlString, typeReference);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static JsonNode deserialize(final String yamlString) {
    try {
      return OBJECT_MAPPER.readTree(yamlString);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static AutoCloseableIterator<JsonNode> deserializeArray(final InputStream stream) {
    try {
      final YAMLParser parser = YAML_FACTORY.createParser(stream);

      // Check the first token
      if (parser.nextToken() != JsonToken.START_ARRAY) {
        throw new IllegalStateException("Expected content to be an array");
      }

      final Iterator<JsonNode> iterator = new AbstractIterator<>() {

        @Override
        protected JsonNode computeNext() {
          try {
            while (parser.nextToken() != JsonToken.END_ARRAY) {
              return parser.readValueAsTree();
            }
          } catch (final IOException e) {
            throw new RuntimeException(e);
          }
          return endOfData();
        }

      };

      return AutoCloseableIterators.fromIterator(iterator, parser::close, null);

    } catch (final IOException e) {
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
  public static <T> CloseableConsumer<T> listWriter(final Writer writer) {
    return new YamlConsumer<>(writer, OBJECT_MAPPER);
  }

  public static class YamlConsumer<T> implements CloseableConsumer<T> {

    private final SequenceWriter sequenceWriter;

    public YamlConsumer(final Writer writer, final ObjectMapper objectMapper) {
      this.sequenceWriter = Exceptions.toRuntime(() -> objectMapper.writer().writeValuesAsArray(writer));

    }

    @Override
    public void accept(final T t) {
      try {
        sequenceWriter.write(t);
      } catch (final IOException e) {
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
