/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TiDBSourceTests {

  private JsonNode config;
  private GenericContainer container;

  @Test
  public void testSettingTimezones() throws Exception {
    container = new GenericContainer(DockerImageName.parse("pingcap/tidb:v5.4.0"))
        .withExposedPorts(4000);

    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", "127.0.0.1")
        .put("port", container.getFirstMappedPort())
        .put("username", "root")
        .put("database", "test")
        .build());

    AirbyteConnectionStatus check = new TiDBSource().check(config);

    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check.getStatus());
    container.close();
  }

}
