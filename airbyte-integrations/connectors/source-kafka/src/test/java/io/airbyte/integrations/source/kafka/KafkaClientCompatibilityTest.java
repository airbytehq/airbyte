/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.kafka.format.JsonFormat;
import java.util.Map;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.config.SaslConfigs;
import org.apache.kafka.common.config.internals.BrokerSecurityConfigs;
import org.apache.kafka.common.security.JaasContext;
import org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginCallbackHandler;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;

class KafkaClientCompatibilityTest {

  @ParameterizedTest
  @ValueSource(strings = {"default", "use_all_dns_ips", "resolve_canonical_bootstrap_servers_only"})
  void acceptsSavedDnsLookupSettings(final String dnsLookup) throws Exception {
    final ObjectNode config = (ObjectNode) Jsons.deserialize(MoreResources.readResource("test_config.json"));
    config.put("client_dns_lookup", dnsLookup);
    final ConsumerConfig consumerConfig = new ConsumerConfig(new TestJsonFormat(config).properties());
    assertEquals("default".equals(dnsLookup) ? "use_all_dns_ips" : dnsLookup,
        consumerConfig.getString(ConsumerConfig.CLIENT_DNS_LOOKUP_CONFIG));
    assertEquals(dnsLookup, config.get("client_dns_lookup").asText());
  }

  @ParameterizedTest
  @NullSource
  @ValueSource(strings = {"https://identity.example/token", "https://other.example/token", ""})
  void oauthCallbackRespectsOptionalEndpointAllowlist(final String allowedUrls) throws Exception {
    final String property = BrokerSecurityConfigs.ALLOWED_SASL_OAUTHBEARER_URLS_CONFIG;
    final String original = System.getProperty(property);
    final OAuthBearerLoginCallbackHandler handler = new OAuthBearerLoginCallbackHandler();
    try {
      if (allowedUrls == null) {
        System.clearProperty(property);
      } else {
        System.setProperty(property, allowedUrls);
      }
      final ObjectNode config = (ObjectNode) Jsons.deserialize(MoreResources.readResource("test_config.json"));
      final ObjectNode protocol = (ObjectNode) config.get("protocol");
      protocol.put("sasl_mechanism", "OAUTHBEARER");
      protocol.put("sasl_jaas_config",
          "org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required clientId=\"test\" clientSecret=\"test\";");
      protocol.put("oauthbearer_token_endpoint_url", "https://identity.example/token");
      final Map<String, ?> properties = new ConsumerConfig(new TestJsonFormat(config).properties()).values();
      assertEquals(OAuthBearerLoginCallbackHandler.class, properties.get(SaslConfigs.SASL_LOGIN_CALLBACK_HANDLER_CLASS));
      final Runnable configure = () -> handler.configure(properties, "OAUTHBEARER",
          JaasContext.loadClientContext(properties).configurationEntries());
      if (allowedUrls == null || "https://identity.example/token".equals(allowedUrls)) {
        assertDoesNotThrow(configure::run);
      } else {
        assertThrows(IllegalArgumentException.class, configure::run);
      }
      assertEquals(allowedUrls, System.getProperty(property));
    } finally {
      handler.close();
      if (original == null) {
        System.clearProperty(property);
      } else {
        System.setProperty(property, original);
      }
    }
  }

  private static class TestJsonFormat extends JsonFormat {

    TestJsonFormat(final JsonNode config) {
      super(config);
    }

    Map<String, Object> properties() {
      return getKafkaConfig();
    }

  }

}
