/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

public class TiDBSourceTests {

  private JsonNode config;
  private GenericContainer container;

  @Test
  public void testSettingTimezones() throws Exception {
    container = new GenericContainer(DockerImageName.parse("pingcap/tidb:nightly"))
        .withExposedPorts(4000);

    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "127.0.0.1")
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.USERNAME_KEY, "root")
        .put(JdbcUtils.DATABASE_KEY, "test")
        .build());

    final AirbyteConnectionStatus check = new TiDBSource().check(config);

    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check.getStatus());
    container.close();
  }

}
