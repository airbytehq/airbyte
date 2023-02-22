/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.opensearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.opensearch.testcontainers.OpensearchContainer;
import org.testcontainers.containers.Network;

public abstract class SshOpenSearchDestinationAcceptanceTest extends OpenSearchDestinationAcceptanceTest {

  private static final Network network = Network.newNetwork();
  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static OpensearchContainer container;
  private ObjectMapper mapper = new ObjectMapper();
  private final static String ELASTIC_PASSWORD = "MagicWord";

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  private String getEndPoint() {
    return String.format("http://%s",
        container.getHttpHostAddress());
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
    container = new OpensearchContainer("opensearchproject/opensearch:2.5.0")
        .withNetwork(network);
    container.start();
  }

  @AfterAll
  public static void afterAll() {
    container.close();
    bastion.getContainer().close();
  }

}
