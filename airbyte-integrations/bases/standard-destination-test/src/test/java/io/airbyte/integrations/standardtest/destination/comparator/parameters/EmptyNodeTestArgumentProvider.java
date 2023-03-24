package io.airbyte.integrations.standardtest.destination.comparator.parameters;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.stream.Stream;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;

public class EmptyNodeTestArgumentProvider implements ArgumentsProvider {

  static ObjectMapper mapper = new ObjectMapper();

  @Override
  public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
    return Stream.of(
        Arguments.of(null, true),
        Arguments.of(mapper.readTree(""), true),
        Arguments.of(mapper.readTree("{}"), true),
        Arguments.of(mapper.readTree("{\"\":\"\"}"), true),
        Arguments.of(mapper.readTree("{\"foo\":0}"), false)
    );
  }
}
