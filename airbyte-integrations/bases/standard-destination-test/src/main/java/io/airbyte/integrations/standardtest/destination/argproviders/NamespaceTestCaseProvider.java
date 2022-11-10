/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.argproviders;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import java.util.stream.Stream;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;

public class NamespaceTestCaseProvider implements ArgumentsProvider {

  public static final String NAMESPACE_TEST_CASES_JSON = "namespace_test_cases.json";

  @Override
  public Stream<? extends Arguments> provideArguments(final ExtensionContext context)
      throws Exception {
    final JsonNode testCases =
        Jsons.deserialize(MoreResources.readResource(NAMESPACE_TEST_CASES_JSON));
    return MoreIterators.toList(testCases.elements()).stream()
        .filter(testCase -> testCase.get("enabled").asBoolean())
        .map(testCase -> Arguments.of(
            testCase.get("id").asText(),
            testCase.get("namespace").asText(),
            testCase.get("normalized").asText()));
  }

}
