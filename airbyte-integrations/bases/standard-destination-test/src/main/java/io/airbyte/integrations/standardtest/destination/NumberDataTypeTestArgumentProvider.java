/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import java.util.stream.Stream;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;

public class NumberDataTypeTestArgumentProvider implements ArgumentsProvider {

  public static final String NUMBER_DATA_TYPE_TEST_CATALOG = "number_data_type_test_catalog.json";
  public static final String NUMBER_DATA_TYPE_TEST_MESSAGES = "number_data_type_test_messages.txt";
  public static final String NUMBER_DATA_TYPE_ARRAY_TEST_CATALOG = "number_data_type_array_test_catalog.json";
  public static final String NUMBER_DATA_TYPE_ARRAY_TEST_MESSAGES = "number_data_type_array_test_messages.txt";

  @Override
  public Stream<? extends Arguments> provideArguments(ExtensionContext context) {
    return Stream.of(
        Arguments.of(NUMBER_DATA_TYPE_TEST_CATALOG, NUMBER_DATA_TYPE_TEST_MESSAGES),
        Arguments.of(NUMBER_DATA_TYPE_ARRAY_TEST_CATALOG, NUMBER_DATA_TYPE_ARRAY_TEST_MESSAGES));
  }

}
