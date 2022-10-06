/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.logging;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.constants.AirbyteSecretConstants;
import io.airbyte.commons.json.Jsons;
import org.apache.logging.log4j.core.LogEvent;
import org.apache.logging.log4j.message.Message;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link MaskedDataInterceptor} Log4j rewrite policy.
 */
class MaskedDataInterceptorTest {

  private static final String FOO = "foo";
  private static final String OTHER = "other";
  private static final String JSON_WITH_STRING_SECRETS = "{\"" + FOO + "\":\"test\",\"" + OTHER + "\":{\"prop\":\"value\",\"bar\":\"1234\"}}";
  private static final String JSON_WITH_STRING_WITH_QUOTE_SECRETS =
      "{\"" + FOO + "\":\"\\\"test\\\"\",\"" + OTHER + "\":{\"prop\":\"value\",\"bar\":\"1234\"}}";
  private static final String JSON_WITH_NUMBER_SECRETS = "{\"" + FOO + "\":\"test\",\"" + OTHER + "\":{\"prop\":\"value\",\"bar\":1234}}";
  private static final String JSON_WITHOUT_SECRETS = "{\"prop1\":\"test\",\"" + OTHER + "\":{\"prop2\":\"value\",\"prop3\":1234}}";
  public static final String TEST_SPEC_SECRET_MASK_YAML = "/test_spec_secret_mask.yaml";

  @Test
  void testMaskingMessageWithStringSecret() {
    final Message message = mock(Message.class);
    final LogEvent logEvent = mock(LogEvent.class);
    when(message.getFormattedMessage()).thenReturn(JSON_WITH_STRING_SECRETS);
    when(logEvent.getMessage()).thenReturn(message);

    final MaskedDataInterceptor interceptor = MaskedDataInterceptor.createPolicy(TEST_SPEC_SECRET_MASK_YAML);

    final LogEvent result = interceptor.rewrite(logEvent);

    final JsonNode json = Jsons.deserialize(result.getMessage().getFormattedMessage());
    assertEquals(AirbyteSecretConstants.SECRETS_MASK, json.get(FOO).asText());
    assertEquals(AirbyteSecretConstants.SECRETS_MASK, json.get(OTHER).get("bar").asText());
  }

  @Test
  void testMaskingMessageWithStringSecretWithQuotes() {
    final Message message = mock(Message.class);
    final LogEvent logEvent = mock(LogEvent.class);
    when(message.getFormattedMessage()).thenReturn(JSON_WITH_STRING_WITH_QUOTE_SECRETS);
    when(logEvent.getMessage()).thenReturn(message);

    final MaskedDataInterceptor interceptor = MaskedDataInterceptor.createPolicy(TEST_SPEC_SECRET_MASK_YAML);
    final LogEvent result = interceptor.rewrite(logEvent);

    final JsonNode json = Jsons.deserialize(result.getMessage().getFormattedMessage());
    assertEquals(AirbyteSecretConstants.SECRETS_MASK, json.get(FOO).asText());
    assertEquals(AirbyteSecretConstants.SECRETS_MASK, json.get(OTHER).get("bar").asText());
  }

  @Test
  void testMaskingMessageWithNumberSecret() {
    final Message message = mock(Message.class);
    final LogEvent logEvent = mock(LogEvent.class);
    when(message.getFormattedMessage()).thenReturn(JSON_WITH_NUMBER_SECRETS);
    when(logEvent.getMessage()).thenReturn(message);

    final MaskedDataInterceptor interceptor = MaskedDataInterceptor.createPolicy(TEST_SPEC_SECRET_MASK_YAML);

    final LogEvent result = interceptor.rewrite(logEvent);

    final JsonNode json = Jsons.deserialize(result.getMessage().getFormattedMessage());
    assertEquals(AirbyteSecretConstants.SECRETS_MASK, json.get(FOO).asText());
    assertEquals(AirbyteSecretConstants.SECRETS_MASK, json.get(OTHER).get("bar").asText());
  }

  @Test
  void testMaskingMessageWithoutSecret() {
    final Message message = mock(Message.class);
    final LogEvent logEvent = mock(LogEvent.class);
    when(message.getFormattedMessage()).thenReturn(JSON_WITHOUT_SECRETS);
    when(logEvent.getMessage()).thenReturn(message);

    final MaskedDataInterceptor interceptor = MaskedDataInterceptor.createPolicy(TEST_SPEC_SECRET_MASK_YAML);

    final LogEvent result = interceptor.rewrite(logEvent);

    final JsonNode json = Jsons.deserialize(result.getMessage().getFormattedMessage());
    assertNotEquals(AirbyteSecretConstants.SECRETS_MASK, json.get("prop1").asText());
    assertNotEquals(AirbyteSecretConstants.SECRETS_MASK, json.get(OTHER).get("prop2").asText());
    assertNotEquals(AirbyteSecretConstants.SECRETS_MASK, json.get(OTHER).get("prop3").asText());
  }

  @Test
  void testMaskingMessageThatDoesNotMatchPattern() {
    final String actualMessage = "This is some log message that doesn't match the pattern.";
    final Message message = mock(Message.class);
    final LogEvent logEvent = mock(LogEvent.class);
    when(message.getFormattedMessage()).thenReturn(actualMessage);
    when(logEvent.getMessage()).thenReturn(message);

    final MaskedDataInterceptor interceptor = MaskedDataInterceptor.createPolicy(TEST_SPEC_SECRET_MASK_YAML);

    final LogEvent result = interceptor.rewrite(logEvent);
    assertFalse(result.getMessage().getFormattedMessage().contains(AirbyteSecretConstants.SECRETS_MASK));
    assertEquals(actualMessage, result.getMessage().getFormattedMessage());
  }

  @Test
  void testMissingMaskingFileDoesNotPreventLogging() {
    final Message message = mock(Message.class);
    final LogEvent logEvent = mock(LogEvent.class);
    when(message.getFormattedMessage()).thenReturn(JSON_WITHOUT_SECRETS);
    when(logEvent.getMessage()).thenReturn(message);

    assertDoesNotThrow(() -> {
      final MaskedDataInterceptor interceptor = MaskedDataInterceptor.createPolicy("/does_not_exist.yaml");
      final LogEvent result = interceptor.rewrite(logEvent);
      assertEquals(JSON_WITHOUT_SECRETS, result.getMessage().getFormattedMessage());
    });
  }

}
