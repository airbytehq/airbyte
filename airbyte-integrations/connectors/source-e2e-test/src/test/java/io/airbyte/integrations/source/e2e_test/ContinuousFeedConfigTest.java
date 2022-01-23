package io.airbyte.integrations.source.e2e_test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.validation.json.JsonValidationException;
import java.util.Optional;
import java.util.Random;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class ContinuousFeedConfigTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(ContinuousFeedConfigTest.class);

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();
  private static final Random RANDOM = new Random();

  @Test
  public void testParseSeed() {
    final long seed = RANDOM.nextLong();
    assertEquals(seed, ContinuousFeedConfig.parseSeed(Jsons.deserialize(String.format("{ \"seed\": %d }", seed))));
  }

  @Test
  public void testParseMaxMessages() {
    final long maxMessages = RANDOM.nextLong();
    assertEquals(maxMessages, ContinuousFeedConfig.parseMaxMessages(Jsons.deserialize(String.format("{ \"max_messages\": %d }", maxMessages))));
  }

  @Test
  public void testParseMessageIntervalMs() {
    assertEquals(Optional.empty(), ContinuousFeedConfig.parseMessageIntervalMs(Jsons.deserialize("{}")));
    assertEquals(Optional.empty(), ContinuousFeedConfig.parseMessageIntervalMs(Jsons.deserialize("{ \"message_interval_ms\": -1 }")));
    assertEquals(Optional.empty(), ContinuousFeedConfig.parseMessageIntervalMs(Jsons.deserialize("{ \"message_interval_ms\": 0 }")));
    assertEquals(Optional.of(999L), ContinuousFeedConfig.parseMessageIntervalMs(Jsons.deserialize("{ \"message_interval_ms\": 999 }")));
  }

  public static class ContinuousFeedConfigTestCaseProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
      final JsonNode testCases =
          Jsons.deserialize(MoreResources.readResource("parse_mock_catalog_test_cases.json"));
      return MoreIterators.toList(testCases.elements()).stream().map(testCase -> {
        final JsonNode sourceConfig = MAPPER.createObjectNode().set("mock_catalog", testCase.get("mockCatalog"));
        final boolean invalidSchema = testCase.has("invalidSchema") && testCase.get("invalidSchema").asBoolean();
        final AirbyteCatalog expectedCatalog = invalidSchema ? null : Jsons.object(testCase.get("expectedCatalog"), AirbyteCatalog.class);
        return Arguments.of(
            testCase.get("testCase").asText(),
            sourceConfig,
            invalidSchema,
            expectedCatalog);
      });
    }

  }

  @ParameterizedTest
  @ArgumentsSource(ContinuousFeedConfigTestCaseProvider.class)
  public void testParseMockCatalog(final String testCaseName,
                                   final JsonNode mockConfig,
                                   final boolean invalidSchema,
                                   final AirbyteCatalog expectedCatalog) throws Exception {
    if (invalidSchema) {
      assertThrows(JsonValidationException.class, () -> ContinuousFeedConfig.parseMockCatalog(mockConfig));
    } else {
      final AirbyteCatalog actualCatalog = ContinuousFeedConfig.parseMockCatalog(mockConfig);
      assertEquals(expectedCatalog.getStreams(), actualCatalog.getStreams());
    }
  }

}
