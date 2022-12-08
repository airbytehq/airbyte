/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.testcontainers.containers.Network;
import org.testcontainers.elasticsearch.ElasticsearchContainer;

public abstract class SshElasticsearchDestinationAcceptanceTest extends ElasticsearchDestinationAcceptanceTest {

  private static final Network network = Network.newNetwork();
  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static ElasticsearchContainer container;
  private ObjectMapper mapper = new ObjectMapper();
  private final static String ELASTIC_PASSWORD = "MagicWord";

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  private String getEndPoint() {
    return String.format("http://%s:%d",
        container.getContainerInfo().getNetworkSettings()
            .getNetworks()
            .entrySet().stream().findFirst().get().getValue().getIpAddress(),
        container.getExposedPorts().get(0));
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder().put("endpoint", getEndPoint())
        .put("upsert", false)
        .put("authenticationMethod", Jsons.jsonNode(ImmutableMap.builder().put("method", "basic")
            .put("username", "elastic")
            .put("password", ELASTIC_PASSWORD).build())));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    // should result in a failed connection check
    return bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder().put("endpoint", getEndPoint())
        .put("upsert", true)
        .put("authenticationMethod", Jsons.jsonNode(ImmutableMap.builder().put("method", "basic")
            .put("username", "elastic")
            .put("password", "wrongpassword").build())));
  }

  @BeforeAll
  public static void beforeAll() {
    bastion.initAndStartBastion(network);
    container = new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:7.15.1")
        .withNetwork(network)
        .withPassword(ELASTIC_PASSWORD);
    container.start();
  }

  @AfterAll
  public static void afterAll() {
    container.close();
    bastion.getContainer().close();
  }

}
