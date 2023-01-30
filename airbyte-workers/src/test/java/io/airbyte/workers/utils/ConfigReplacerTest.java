/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.utils;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.config.AllowedHosts;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class ConfigReplacerTest {

  final Logger logger = LoggerFactory.getLogger(ConfigReplacerTest.class);

  final ConfigReplacer replacer = new ConfigReplacer(logger);
  final ObjectMapper mapper = new ObjectMapper();

  @Test
  @SuppressWarnings("PMD.AvoidUsingHardCodedIP")
  void getAllowedHostsGeneralTest() throws IOException {
    final AllowedHosts allowedHosts = new AllowedHosts();
    final List<String> hosts = new ArrayList();
    hosts.add("localhost");
    hosts.add("static-site.com");
    hosts.add("${host}");
    hosts.add("${number}");
    hosts.add("${subdomain}.vendor.com");
    hosts.add("${tunnel_method.tunnel_host}");
    allowedHosts.setHosts(hosts);

    final List<String> expected = new ArrayList<>();
    expected.add("localhost");
    expected.add("static-site.com");
    expected.add("foo.com");
    expected.add("123");
    expected.add("account.vendor.com");
    expected.add("1.2.3.4");

    final String configJson =
        "{\"host\": \"foo.com\", \"number\": 123, \"subdomain\": \"account\", \"password\": \"abc123\", \"tunnel_method\": {\"tunnel_host\": \"1.2.3.4\"}}";
    final JsonNode config = mapper.readValue(configJson, JsonNode.class);
    final AllowedHosts response = replacer.getAllowedHosts(allowedHosts, config);

    assertThat(response.getHosts()).isEqualTo(expected);
  }

  @Test
  void getAllowedHostsNestingTest() throws IOException {
    final AllowedHosts allowedHosts = new AllowedHosts();
    final List<String> hosts = new ArrayList();
    hosts.add("value-${a.b.c.d}");
    allowedHosts.setHosts(hosts);

    final List<String> expected = new ArrayList<>();
    expected.add("value-100");

    final String configJson = "{\"a\": {\"b\": {\"c\": {\"d\": 100 }}}, \"array\": [1,2,3]}";
    final JsonNode config = mapper.readValue(configJson, JsonNode.class);
    final AllowedHosts response = replacer.getAllowedHosts(allowedHosts, config);

    assertThat(response.getHosts()).isEqualTo(expected);
  }

  @Test
  void ensureEmptyArrayRemains() throws IOException {
    final AllowedHosts allowedHosts = new AllowedHosts();
    allowedHosts.setHosts(new ArrayList());
    final List<String> expected = new ArrayList<>();

    final String configJson = "{}";
    final JsonNode config = mapper.readValue(configJson, JsonNode.class);
    final AllowedHosts response = replacer.getAllowedHosts(allowedHosts, config);

    assertThat(response.getHosts()).isEqualTo(expected);
  }

}
