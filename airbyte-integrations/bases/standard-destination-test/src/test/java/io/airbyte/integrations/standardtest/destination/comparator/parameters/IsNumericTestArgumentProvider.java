/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.comparator.parameters;

import java.util.stream.Stream;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;

public class IsNumericTestArgumentProvider implements ArgumentsProvider {

  @Override
  public Stream<? extends Arguments> provideArguments(final ExtensionContext context) {
    return Stream.of(
        Arguments.of("", false),
        Arguments.of("hello world", false),
        Arguments.of("-12 1 . 7", false),
        Arguments.of("1234.", false),
        Arguments.of("1", true),
        Arguments.of("-123", true),
        Arguments.of("-1234567890.0987654321", true),
        Arguments.of("1234567890.0987654321", true));
  }

}
