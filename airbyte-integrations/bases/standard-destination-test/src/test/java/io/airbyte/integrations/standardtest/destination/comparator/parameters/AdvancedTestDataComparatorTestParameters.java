/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.comparator.parameters;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparatorTest;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.IntStream;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AdvancedTestDataComparatorTestParameters {

  static File[] getAllSimpleTestJsonFiles() throws Exception {
    final URL testdata = AdvancedTestDataComparatorTest.class.getClassLoader().getResource("testdata/simple");
    assert testdata != null;
    final File testdataDir = new File(testdata.toURI());
    return Objects.requireNonNull(testdataDir.listFiles());
  }

  static List<JsonNode> getAllSimpleTestJsonNodes() throws Exception {
    final List<JsonNode> nodes = new ArrayList<>();
    for (final File file : getAllSimpleTestJsonFiles()) {
      try (final FileInputStream input = new FileInputStream(file);) {
        nodes.add(objectMapper.readTree(input));
      }
    }
    return nodes;
  }

  static <T> List<T> pairToList(final Pair<T, T> pair) {
    return List.of(pair.getLeft(), pair.getRight());
  }

  final static ObjectMapper objectMapper = new ObjectMapper();

  private static Pair<JsonNode, JsonNode> twoCopiesOfSameFile(final File file) throws Exception {
    try (final FileInputStream json = new FileInputStream(file)) {
      final JsonNode first = objectMapper.readTree(json);
      final JsonNode second = first.deepCopy();
      return Pair.of(first, second);
    }
  }

  public static class AssertSameDataArgumentProvider implements ArgumentsProvider {

    private static final Logger LOGGER = LoggerFactory.getLogger(AssertSameDataArgumentProvider.class);

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) {
      final List<Arguments> arguments = new ArrayList<>();
      try {
        for (final File file : getAllSimpleTestJsonFiles()) {
          if (file.isFile()) {
            final Pair<JsonNode, JsonNode> twoCopies = twoCopiesOfSameFile(file);
            arguments.add(Arguments.of(List.of(twoCopies.getLeft()), List.of(twoCopies.getRight())));
            arguments.add(Arguments.of(pairToList(twoCopies), pairToList(twoCopies)));
          }
        }
      } catch (final Exception e) {
        LOGGER.error("Encountered Error during deserialization of JSON test data", e);
      }
      return arguments.stream();
    }

  }

  public static class AssertNotSameDataArgumentProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
      final JsonNode emptyNode;
      final JsonNode notEmptyNode;
      final List<Arguments> arguments = new ArrayList<>();
      try (final InputStream emptyJson = AdvancedTestDataComparatorTest.class.getClassLoader().getResourceAsStream("testdata/simple/empty.json")) {
        emptyNode = objectMapper.readTree(emptyJson);
      }
      try (final InputStream notEmptyJson = AdvancedTestDataComparatorTest.class.getClassLoader()
          .getResourceAsStream("testdata/simple/not-empty.json")) {
        notEmptyNode = objectMapper.readTree(notEmptyJson);
      }
      arguments.add(Arguments.of(List.of(emptyNode), List.of(notEmptyNode)));
      final List<List<JsonNode>> pairs = Lists.partition(getAllSimpleTestJsonNodes(), 2);
      IntStream.range(0, pairs.size() - 1).forEach(i -> arguments.add(Arguments.of(pairs.get(i), pairs.get(i + 1))));
      return arguments.stream();
    }

  }

}
