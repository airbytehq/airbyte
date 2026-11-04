/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import java.util.Map;
import java.util.stream.StreamSupport;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.MockedStatic;

class KafkaDestinationTest {

  private KafkaDestination destination(final String deployment) {
    return new KafkaDestination(deployment);
  }

  private JsonNode config(final String protocol) {
    return Jsons.jsonNode(Map.of("protocol", Map.of("security_protocol", protocol,
        "sasl_mechanism", "PLAIN",
        "sasl_jaas_config", "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"test\" password=\"test\";")));
  }

  @ParameterizedTest
  @ValueSource(strings = {"CLOUD", "cloud"})
  void cloudSpecOnlyAllowsTls(final String deployment) throws Exception {
    final JsonNode protocols = destination(deployment).spec().getConnectionSpecification().get("properties").get("protocol").get("oneOf");
    assertEquals(1, protocols.size());
    assertEquals("SASL_SSL", protocols.get(0).get("properties").get("security_protocol").get("enum").get(0).asText());
    assertTrue(StreamSupport.stream(protocols.get(0).get("properties").get("sasl_mechanism").get("enum").spliterator(), false)
        .anyMatch(mechanism -> "PLAIN".equals(mechanism.asText())));
  }

  @ParameterizedTest
  @NullAndEmptySource
  @ValueSource(strings = {"OSS", "ENTERPRISE"})
  void nonCloudSpecIsUnchanged(final String deployment) throws Exception {
    assertEquals(Jsons.deserialize(MoreResources.readResource("spec.json")).get("connectionSpecification"),
        destination(deployment).spec().getConnectionSpecification());
  }

  @ParameterizedTest
  @ValueSource(strings = {"PLAINTEXT", "SASL_PLAINTEXT", "SSL", "", "UNKNOWN"})
  void cloudRejectsInsecureProtocolsBeforeConnecting(final String protocol) {
    final KafkaDestination destination = destination("CLOUD");
    final JsonNode config = config(protocol);
    assertThrows(ConfigErrorException.class, () -> destination.check(config));
    assertThrows(ConfigErrorException.class, () -> destination.getConsumer(config, null, null));
  }

  @Test
  void cloudRejectsMissingProtocol() {
    final KafkaDestination destination = destination("CLOUD");
    final JsonNode config = Jsons.emptyObject();
    assertThrows(ConfigErrorException.class, () -> destination.check(config));
    assertThrows(ConfigErrorException.class, () -> destination.getConsumer(config, null, null));
  }

  @ParameterizedTest
  @NullAndEmptySource
  @ValueSource(strings = {
    "com.sun.security.auth.module.JndiLoginModule required;",
    "com.example.CustomLoginModule required;",
    "org.apache.kafka.common.security.plain.PlainLoginModuleSuffix required;",
    "org.apache.kafka.common.security.plain.PlainLoginModule required; com.example.CustomLoginModule required;",
    "org.apache.kafka.common.security.plain.PlainLoginModule required password=\"sensitive-test-value\"",
    "not valid JAAS sensitive-test-value"
  })
  void cloudRejectsUnsupportedOrInvalidJaasBeforeConnecting(final String jaas) {
    final KafkaDestination destination = destination("CLOUD");
    final JsonNode config = config("SASL_SSL");
    final ObjectNode protocol = (ObjectNode) config.get("protocol");
    if (jaas == null) {
      protocol.remove("sasl_jaas_config");
    } else {
      protocol.put("sasl_jaas_config", jaas);
    }
    try (final MockedStatic<KafkaDestinationConfig> factory = mockStatic(KafkaDestinationConfig.class)) {
      final ConfigErrorException error = assertThrows(ConfigErrorException.class, () -> destination.check(config));
      assertFalse(error.getMessage().contains("sensitive-test-value"));
      assertThrows(ConfigErrorException.class, () -> destination.check(config));
      assertThrows(ConfigErrorException.class, () -> destination.getConsumer(config, null, null));
      factory.verifyNoInteractions();
    }
  }

  @Test
  void ossDoesNotValidateLoginModules() throws Exception {
    final KafkaDestination destination = destination("OSS");
    final JsonNode config = config("SASL_SSL");
    ((ObjectNode) config.get("protocol")).put("sasl_jaas_config", "com.example.CustomLoginModule required;");
    final KafkaDestinationConfig producerConfig = mock(KafkaDestinationConfig.class);
    try (final MockedStatic<KafkaDestinationConfig> factory = mockStatic(KafkaDestinationConfig.class)) {
      factory.when(() -> KafkaDestinationConfig.getKafkaDestinationConfig(config)).thenReturn(producerConfig);
      assertEquals(Status.SUCCEEDED, destination.check(config).getStatus());
      assertNotNull(destination.getConsumer(config, null, null));
    }
  }

  @ParameterizedTest
  @ValueSource(strings = {"SASL_SSL", "sasl_ssl"})
  void cloudAllowsSecureOperations(final String protocol) {
    final KafkaDestination destination = destination("CLOUD");
    final JsonNode config = config(protocol);
    final KafkaDestinationConfig producerConfig = mock(KafkaDestinationConfig.class);
    try (final MockedStatic<KafkaDestinationConfig> factory = mockStatic(KafkaDestinationConfig.class)) {
      factory.when(() -> KafkaDestinationConfig.getKafkaDestinationConfig(config)).thenReturn(producerConfig);
      assertEquals(Status.SUCCEEDED, destination.check(config).getStatus());
      assertNotNull(destination.getConsumer(config, null, null));
      factory.verify(() -> KafkaDestinationConfig.getKafkaDestinationConfig(config));
    }
  }

  @ParameterizedTest
  @ValueSource(strings = {"PLAINTEXT", "SASL_PLAINTEXT", "SASL_SSL"})
  void ossAllowsAllExistingProtocols(final String protocol) {
    final KafkaDestination destination = destination("OSS");
    final JsonNode config = config(protocol);
    final KafkaDestinationConfig producerConfig = mock(KafkaDestinationConfig.class);
    try (final MockedStatic<KafkaDestinationConfig> factory = mockStatic(KafkaDestinationConfig.class)) {
      factory.when(() -> KafkaDestinationConfig.getKafkaDestinationConfig(config)).thenReturn(producerConfig);
      assertEquals(Status.SUCCEEDED, destination.check(config).getStatus());
      assertNotNull(destination.getConsumer(config, null, null));
      factory.verify(() -> KafkaDestinationConfig.getKafkaDestinationConfig(config));
    }
  }

}
