/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Stream;
import net.jimblackler.jsongenerator.Configuration;
import net.jimblackler.jsongenerator.Generator;
import net.jimblackler.jsonschemafriend.Schema;
import net.jimblackler.jsonschemafriend.SchemaStore;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;

/**
 * This test ensures the upstream json generator library is working as expected.
 */
public class GeneratorTest {

  private static final JsonSchemaValidator JSON_VALIDATOR = new JsonSchemaValidator();
  private static final Configuration CONFIG = ContinuousFeedConstants.MOCK_JSON_CONFIG;
  private static final ThreadLocalRandom RANDOM = ThreadLocalRandom.current();

  public static class GeneratorSchemaProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
      final JsonNode testCases = Jsons.deserialize(MoreResources.readResource("generator_test_cases.json"));
      return MoreIterators.toList(testCases.elements()).stream().map(testCase -> Arguments.of(
          testCase.get("testCase").asText(),
          testCase.get("schema")));
    }

  }

  @ParameterizedTest
  @ArgumentsSource(GeneratorSchemaProvider.class)
  public void testComplexObjectGeneration(final String testCase, final JsonNode jsonSchema) throws Exception {
    final SchemaStore schemaStore = new SchemaStore(true);
    final Schema schema = schemaStore.loadSchemaJson(Jsons.serialize(jsonSchema));
    final Generator generator = new Generator(CONFIG, schemaStore, RANDOM);
    for (int i = 0; i < 10; ++i) {
      final JsonNode json = Jsons.jsonNode(generator.generate(schema, ContinuousFeedConstants.MOCK_JSON_MAX_TREE_SIZE));
      assertTrue(JSON_VALIDATOR.test(jsonSchema, json), testCase);
    }

  }

}
