package io.airbyte.integrations.standardtest.destination.comparator.parameters;

import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;

public class IsDateTimeWithTzTestArgumentProvider implements ArgumentsProvider {

  @Override
  public Stream<? extends Arguments> provideArguments(final ExtensionContext context) {
    final List<Arguments> arguments = new ArrayList<>();
    AdvancedTestDataComparator.TEST_DATASET_IGNORE_LIST.forEach(dateTimeString -> arguments.add(Arguments.of(dateTimeString, false)));
    arguments.addAll(List.of(
        Arguments.of("", false),
        Arguments.of("hello world", false),
        Arguments.of("-12 1 . 7", false),
        Arguments.of("1234.", false)
    ));
    return arguments.stream();
  }
}
