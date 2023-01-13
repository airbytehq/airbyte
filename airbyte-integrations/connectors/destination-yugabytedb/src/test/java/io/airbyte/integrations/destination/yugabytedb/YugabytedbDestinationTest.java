/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yugabytedb;

import static org.assertj.core.api.Assertions.assertThat;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Collections;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class YugabytedbDestinationTest {

  private YugabytedbDestination yugabytedbDestination;

  @BeforeEach
  void setup() {
    yugabytedbDestination = new YugabytedbDestination();
  }

  @Test
  void testToJdbcConfig() {

    var config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", "localhost")
        .put("port", 5433)
        .put("database", "yugabyte")
        .put("username", "yugabyte")
        .put("password", "yugabyte")
        .put("schema", "public")
        .build());

    var jdbcConfig = yugabytedbDestination.toJdbcConfig(config);

    assertThat(jdbcConfig.get("schema").asText()).isEqualTo("public");
    assertThat(jdbcConfig.get("username").asText()).isEqualTo("yugabyte");
    assertThat(jdbcConfig.get("password").asText()).isEqualTo("yugabyte");
    assertThat(jdbcConfig.get("jdbc_url").asText()).isEqualTo("jdbc:yugabytedb://localhost:5433/yugabyte");

  }

  @Test
  void testGetDefaultConnectionProperties() {

    var map = yugabytedbDestination.getDefaultConnectionProperties(Jsons.jsonNode(Collections.emptyMap()));

    assertThat(map).isEmpty();

  }

}
