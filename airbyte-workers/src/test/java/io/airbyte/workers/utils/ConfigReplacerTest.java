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
  void getAllowedHostsGeneralTest() throws IOException {
    final AllowedHosts allowedHosts = new AllowedHosts();
    final List<String> hosts = new ArrayList();
    hosts.add("localhost");
    hosts.add("static-site.com");
    hosts.add("${host}");
    hosts.add("${subdomain}.vendor.com");
    allowedHosts.setHosts(hosts);

    final List<String> expected = new ArrayList<>();
    expected.add("localhost");
    expected.add("static-site.com");
    expected.add("foo.com");
    expected.add("account.vendor.com");

    final String configJson = "{\"host\": \"foo.com\", \"subdomain\": \"account\", \"password\": \"abc123\"}";
    final JsonNode config = mapper.readValue(configJson, JsonNode.class);
    final AllowedHosts response = replacer.getAllowedHosts(allowedHosts, config);

    assertThat(response.getHosts()).isEqualTo(expected);
  }

}
