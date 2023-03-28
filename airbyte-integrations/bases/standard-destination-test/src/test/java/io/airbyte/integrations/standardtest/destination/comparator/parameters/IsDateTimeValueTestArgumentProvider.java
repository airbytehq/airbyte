/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.comparator.parameters;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;

public class IsDateTimeValueTestArgumentProvider implements ArgumentsProvider {

  // "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?( BC)?$"
  private static final List<String> shouldMatch = List.of(
      "2023-08-29T00:00:00",
      "2023-09-15T16:58:52.000000",
      "2023-08-29T00:00:00 BC",
      "2023-09-15T16:58:52.000000 BC");

  private static final List<String> shouldNotMatch = List.of(
      "",
      "hello world",
      "1234:08:29T00:00:00Z",
      "2023-12-32T12:99:88+1:23",
      "2023-12-32T12:99:88+12:23",
      "2023-12-32T12:99:88-1:23",
      "2023-12-32T12:99:88-31:23",
      "2023-08-29T00:00:00Z BC",
      "2023-09-15T16:58:52.000000Z BC",
      "2023-12-32T12:99:88+1:23 BC",
      "2023-12-32T12:99:88+12:23 BC",
      "2023-12-32T12:99:88-1:23 BC",
      "2023-12-32T12:99:88-31:23 BC");

  @Override
  public Stream<? extends Arguments> provideArguments(final ExtensionContext context) {
    final List<Arguments> arguments = new ArrayList<>();
    shouldMatch.forEach(dateTimeString -> arguments.add(Arguments.of(dateTimeString, true)));
    shouldNotMatch.forEach(dateTimeString -> arguments.add(Arguments.of(dateTimeString, false)));
    return arguments.stream();
  }

}
