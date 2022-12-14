/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.redis.RedisContainerInitializr.RedisContainer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.integrations.util.HostPortResolver;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.testcontainers.containers.Network;

public abstract class SshRedisDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static final Network network = Network.newNetwork();
  private static RedisContainerInitializr.RedisContainer redisContainer;
  private JsonNode jsonConfig;
  private RedisCache redisCache;
  private RedisNameTransformer redisNameTransformer;

  @BeforeAll
  static void initContainers() {
    redisContainer = new RedisContainer()
        .withExposedPorts(6379)
        .withNetwork(network);
    redisContainer.start();
    bastion.initAndStartBastion(network);
  }

  @AfterAll
  static void stop() {
    redisContainer.close();
    bastion.stopAndClose();
  }

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    jsonConfig = RedisDataFactory.jsonConfig(
        redisContainer.getHost(),
        redisContainer.getFirstMappedPort());
    redisCache = new RedisHCache(jsonConfig);
    redisNameTransformer = new RedisNameTransformer();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    redisCache.flushAll();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-redis:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder()
        .put("host", HostPortResolver.resolveIpAddress(redisContainer))
        .put("port", redisContainer.getExposedPorts().get(0))
        .put("username", jsonConfig.get("username"))
        .put("password", jsonConfig.get("password"))
        .put("cache_type", jsonConfig.get("cache_type")));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return RedisDataFactory.jsonConfig(
        "127.0.0.9",
        8080);
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema) {
    var key = redisNameTransformer.keyName(namespace, streamName);
    return redisCache.getAll(key).stream()
        .sorted(Comparator.comparing(RedisRecord::getTimestamp))
        .map(RedisRecord::getData)
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

}
