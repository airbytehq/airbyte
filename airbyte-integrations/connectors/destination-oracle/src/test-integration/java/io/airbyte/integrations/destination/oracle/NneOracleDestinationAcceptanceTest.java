/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class NneOracleDestinationAcceptanceTest extends UnencryptedOracleDestinationAcceptanceTest {

  @Test
  public void testEncryption() throws SQLException {
    final String algorithm = "AES256";

    final JsonNode config = getConfig();
    ((ObjectNode) config).put("encryption", Jsons.jsonNode(ImmutableMap.builder()
        .put("encryption_method", "client_nne")
        .put("encryption_algorithm", algorithm)
        .build()));

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get("username").asText(),
            config.get("password").asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get("host").asText(),
                config.get("port").asInt(),
                config.get("sid").asText()),
            getAdditionalProperties(algorithm)));

    final String networkServiceBanner =
        "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertThat(collect.get(2).get("NETWORK_SERVICE_BANNER").asText(),
        is(equalTo("AES256 Encryption service adapter for Linux: Version 18.0.0.0.0 - Production")));
  }

  private Map<String, String> getAdditionalProperties(final String algorithm) {
    return ImmutableMap.of("oracle.net.encryption_client", "REQUIRED",
        "oracle.net.encryption_types_client", String.format("( %s )", algorithm));
  }

  @Test
  public void testCheckProtocol() throws SQLException {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("encryption", Jsons.jsonNode(ImmutableMap.builder()
        .put("encryption_method", "client_nne")
        .put("encryption_algorithm", "AES256")
        .build()));

    final String algorithm = clone.get("encryption")
        .get("encryption_algorithm").asText();

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            clone.get("username").asText(),
            clone.get("password").asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                clone.get("host").asText(),
                clone.get("port").asInt(),
                clone.get("sid").asText()),
            getAdditionalProperties(algorithm)));

    final String networkServiceBanner = "SELECT sys_context('USERENV', 'NETWORK_PROTOCOL') as network_protocol FROM dual";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertEquals("tcp", collect.get(0).get("NETWORK_PROTOCOL").asText());
  }

}
