/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.kafka.format.AvroFormat;
import io.airbyte.integrations.source.kafka.format.KafkaFormat;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.List;
import java.util.stream.StreamSupport;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.MockedStatic;

public class KafkaSourceTest {

  private KafkaSource source(final String deployment) {
    final FeatureFlags featureFlags = mock(FeatureFlags.class);
    when(featureFlags.deploymentMode()).thenReturn(deployment);
    return new KafkaSource(featureFlags);
  }

  private JsonNode config(final String protocol) {
    return Jsons.jsonNode(java.util.Map.of("protocol", java.util.Map.of("security_protocol", protocol,
        "sasl_mechanism", "PLAIN",
        "sasl_jaas_config", "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"test\" password=\"test\";")));
  }

  @ParameterizedTest
  @ValueSource(strings = {"CLOUD", "cloud"})
  void cloudSpecOnlyAllowsTls(final String deployment) throws Exception {
    final JsonNode protocols = source(deployment).spec().getConnectionSpecification().get("properties").get("protocol").get("oneOf");
    assertEquals(1, protocols.size());
    assertEquals("SASL_SSL", protocols.get(0).get("properties").get("security_protocol").get("const").asText());
    assertTrue(StreamSupport.stream(protocols.get(0).get("properties").get("sasl_mechanism").get("enum").spliterator(), false)
        .anyMatch(mechanism -> "PLAIN".equals(mechanism.asText())));
  }

  @ParameterizedTest
  @NullAndEmptySource
  @ValueSource(strings = {"OSS", "ENTERPRISE"})
  void nonCloudSpecIsUnchanged(final String deployment) throws Exception {
    assertEquals(Jsons.deserialize(MoreResources.readResource("spec.json")).get("connectionSpecification"),
        source(deployment).spec().getConnectionSpecification());
  }

  @ParameterizedTest
  @ValueSource(strings = {"PLAINTEXT", "SASL_PLAINTEXT", "SSL", "", "UNKNOWN"})
  void cloudRejectsInsecureProtocolsBeforeConnecting(final String protocol) {
    final KafkaSource source = source("CLOUD");
    final JsonNode config = config(protocol);
    assertThrows(ConfigErrorException.class, () -> source.check(config));
    assertThrows(ConfigErrorException.class, () -> source.discover(config));
    assertThrows(ConfigErrorException.class, () -> source.read(config, new ConfiguredAirbyteCatalog().withStreams(List.of()), null));
  }

  @Test
  void cloudRejectsMissingProtocol() {
    final KafkaSource source = source("CLOUD");
    final JsonNode config = Jsons.emptyObject();
    assertThrows(ConfigErrorException.class, () -> source.check(config));
    assertThrows(ConfigErrorException.class, () -> source.discover(config));
    assertThrows(ConfigErrorException.class, () -> source.read(config, new ConfiguredAirbyteCatalog().withStreams(List.of()), null));
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
    final KafkaSource source = source("CLOUD");
    final JsonNode config = config("SASL_SSL");
    final ObjectNode protocol = (ObjectNode) config.get("protocol");
    if (jaas == null) {
      protocol.remove("sasl_jaas_config");
    } else {
      protocol.put("sasl_jaas_config", jaas);
    }
    try (final MockedStatic<KafkaFormatFactory> factory = mockStatic(KafkaFormatFactory.class)) {
      final ConfigErrorException error = assertThrows(ConfigErrorException.class, () -> source.check(config));
      assertFalse(error.getMessage().contains("sensitive-test-value"));
      assertThrows(ConfigErrorException.class, () -> source.check(config));
      assertThrows(ConfigErrorException.class, () -> source.discover(config));
      assertThrows(ConfigErrorException.class, () -> source.read(config, new ConfiguredAirbyteCatalog().withStreams(List.of()), null));
      factory.verifyNoInteractions();
    }
  }

  @Test
  void ossDoesNotValidateLoginModules() throws Exception {
    final KafkaSource source = source("OSS");
    final JsonNode config = config("SASL_SSL");
    ((ObjectNode) config.get("protocol")).put("sasl_jaas_config", "com.example.CustomLoginModule required;");
    final KafkaFormat format = mock(KafkaFormat.class);
    when(format.isAccessible()).thenReturn(true);
    when(format.getStreams()).thenReturn(List.of());
    try (final MockedStatic<KafkaFormatFactory> factory = mockStatic(KafkaFormatFactory.class)) {
      factory.when(() -> KafkaFormatFactory.getFormat(config)).thenReturn(format);
      assertEquals(Status.SUCCEEDED, source.check(config).getStatus());
      source.discover(config);
      source.read(config, new ConfiguredAirbyteCatalog().withStreams(List.of()), null);
    }
  }

  @ParameterizedTest
  @ValueSource(strings = {"SASL_SSL", "sasl_ssl"})
  void cloudAllowsSecureOperations(final String protocol) throws Exception {
    final KafkaSource source = source("CLOUD");
    final JsonNode config = config(protocol);
    final KafkaFormat format = mock(KafkaFormat.class);
    when(format.isAccessible()).thenReturn(true);
    when(format.getStreams()).thenReturn(List.of());
    try (final MockedStatic<KafkaFormatFactory> factory = mockStatic(KafkaFormatFactory.class)) {
      factory.when(() -> KafkaFormatFactory.getFormat(config)).thenReturn(format);
      assertEquals(Status.SUCCEEDED, source.check(config).getStatus());
      assertEquals(new AirbyteCatalog().withStreams(List.of()), source.discover(config));
      source.read(config, new ConfiguredAirbyteCatalog().withStreams(List.of()), null);
      verify(format).read();
    }
  }

  @ParameterizedTest
  @ValueSource(strings = {"PLAINTEXT", "SASL_PLAINTEXT", "SASL_SSL"})
  void ossAllowsAllExistingProtocols(final String protocol) throws Exception {
    final KafkaSource source = source("OSS");
    final JsonNode config = config(protocol);
    final KafkaFormat format = mock(KafkaFormat.class);
    when(format.isAccessible()).thenReturn(true);
    when(format.getStreams()).thenReturn(List.of());
    try (final MockedStatic<KafkaFormatFactory> factory = mockStatic(KafkaFormatFactory.class)) {
      factory.when(() -> KafkaFormatFactory.getFormat(config)).thenReturn(format);
      assertEquals(Status.SUCCEEDED, source.check(config).getStatus());
      source.discover(config);
      source.read(config, new ConfiguredAirbyteCatalog().withStreams(List.of()), null);
      verify(format).read();
    }
  }

  @Test
  public void testAvroformat() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
    final KafkaFormat kafkaFormat = KafkaFormatFactory.getFormat(configJson);
    assertInstanceOf(AvroFormat.class, kafkaFormat);
  }

  @ParameterizedTest
  @NullAndEmptySource
  @ValueSource(strings = {"http://identity.example/token", "file:/tmp/token", "not a URL",
    "https://user:password@identity.example/token", "https://identity.example/token#fragment"})
  void cloudRejectsUnsafeOAuthTokenEndpoints(final String endpoint) {
    final KafkaSource source = source("CLOUD");
    final JsonNode config = config("SASL_SSL");
    final ObjectNode protocol = (ObjectNode) config.get("protocol");
    protocol.put("sasl_mechanism", "OAUTHBEARER");
    protocol.put("oauthbearer_token_endpoint_url", endpoint);
    try (final MockedStatic<KafkaFormatFactory> factory = mockStatic(KafkaFormatFactory.class)) {
      assertThrows(ConfigErrorException.class, () -> source.check(config));
      assertThrows(ConfigErrorException.class, () -> source.discover(config));
      assertThrows(ConfigErrorException.class, () -> source.read(config, new ConfiguredAirbyteCatalog().withStreams(List.of()), null));
      factory.verifyNoInteractions();
    }
  }

  @ParameterizedTest
  @CsvSource({
    "PLAIN, org.apache.kafka.common.security.plain.PlainLoginModule",
    "SCRAM-SHA-256, org.apache.kafka.common.security.scram.ScramLoginModule",
    "SCRAM-SHA-512, org.apache.kafka.common.security.scram.ScramLoginModule",
    "GSSAPI, com.sun.security.auth.module.Krb5LoginModule",
    "OAUTHBEARER, org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule",
    "AWS_MSK_IAM, software.amazon.msk.auth.iam.IAMLoginModule"
  })
  void cloudAllowsSupportedLoginModules(final String mechanism, final String loginModule) throws Exception {
    final KafkaSource source = source("CLOUD");
    final JsonNode config = config("SASL_SSL");
    final ObjectNode protocol = (ObjectNode) config.get("protocol");
    protocol.put("sasl_mechanism", mechanism);
    protocol.put("oauthbearer_token_endpoint_url", "https://identity.example/token");
    protocol.put("sasl_jaas_config", loginModule + " required password=\"a; quoted value\";");
    final KafkaFormat format = mock(KafkaFormat.class);
    when(format.isAccessible()).thenReturn(true);
    when(format.getStreams()).thenReturn(List.of());
    try (final MockedStatic<KafkaFormatFactory> factory = mockStatic(KafkaFormatFactory.class)) {
      factory.when(() -> KafkaFormatFactory.getFormat(config)).thenReturn(format);
      assertEquals(Status.SUCCEEDED, source.check(config).getStatus());
      source.discover(config);
      source.read(config, new ConfiguredAirbyteCatalog().withStreams(List.of()), null);
      verify(format).read();
    }
  }

  @ParameterizedTest
  @ValueSource(strings = {"http://identity.example/token", "file:/tmp/token"})
  void nonCloudAllowsLegacyOAuthEndpoints(final String endpoint) throws Exception {
    final KafkaSource source = source("OSS");
    final JsonNode config = config("SASL_SSL");
    final ObjectNode protocol = (ObjectNode) config.get("protocol");
    protocol.put("sasl_mechanism", "OAUTHBEARER");
    protocol.put("oauthbearer_token_endpoint_url", endpoint);
    final KafkaFormat format = mock(KafkaFormat.class);
    when(format.isAccessible()).thenReturn(true);
    when(format.getStreams()).thenReturn(List.of());
    try (final MockedStatic<KafkaFormatFactory> factory = mockStatic(KafkaFormatFactory.class)) {
      factory.when(() -> KafkaFormatFactory.getFormat(config)).thenReturn(format);
      assertEquals(Status.SUCCEEDED, source.check(config).getStatus());
      source.discover(config);
      source.read(config, new ConfiguredAirbyteCatalog().withStreams(List.of()), null);
      verify(format).read();
    }
  }

}
