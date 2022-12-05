/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.util.HostPortResolver;
import java.util.ArrayList;
import java.util.List;
import org.bson.Document;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.containers.Network;

public abstract class SshMongoDbDestinationAcceptanceTest extends MongodbDestinationAcceptanceTest {

  private static final Network network = Network.newNetwork();
  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static MongoDBContainer container;
  private static final int DEFAULT_PORT = 27017;

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    container = new MongoDBContainer(DOCKER_IMAGE_NAME)
        .withNetwork(network)
        .withExposedPorts(DEFAULT_PORT);
    container.start();
    bastion.initAndStartBastion(network);
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveIpAddress(container))
        .put(JdbcUtils.PORT_KEY, container.getExposedPorts().get(0))
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put(AUTH_TYPE, getAuthTypeConfig()));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    // should result in a failed connection check
    return bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveIpAddress(container))
        .put(JdbcUtils.PORT_KEY, container.getExposedPorts().get(0))
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put(AUTH_TYPE, Jsons.jsonNode(ImmutableMap.builder()
            .put("authorization", "login/password")
            .put(JdbcUtils.USERNAME_KEY, "user")
            .put(JdbcUtils.PASSWORD_KEY, "invalid_pass")
            .build())));
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    final MongoDatabase database = getMongoDatabase(HostPortResolver.resolveIpAddress(container),
        container.getExposedPorts().get(0), DATABASE_NAME);
    final var collection = database.getOrCreateNewCollection(namingResolver.getRawTableName(streamName));
    final List<JsonNode> result = new ArrayList<>();
    try (final MongoCursor<Document> cursor = collection.find().projection(excludeId()).iterator()) {
      while (cursor.hasNext()) {
        result.add(Jsons.jsonNode(cursor.next().get(AIRBYTE_DATA)));
      }
    }
    return result;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.stop();
    container.close();
    bastion.getContainer().stop();
    bastion.getContainer().close();
  }

}
