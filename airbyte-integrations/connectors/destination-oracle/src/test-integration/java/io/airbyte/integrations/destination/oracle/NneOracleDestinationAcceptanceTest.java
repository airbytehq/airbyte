/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.junit.Test;

public class NneOracleDestinationAcceptanceTest extends UnencryptedOracleDestinationAcceptanceTest {

  @Test
  public void testEncryption() throws SQLException {
    final String algorithm = "AES256";

    final JsonNode config = getConfig();
    ((ObjectNode) config).put("encryption", Jsons.jsonNode(ImmutableMap.builder()
        .put("encryption_method", "client_nne")
        .put("encryption_algorithm", algorithm)
        .build()));

    final JdbcDatabase database = Databases.createJdbcDatabase(config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:oracle:thin:@//%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("sid").asText()),
        "oracle.jdbc.driver.OracleDriver",
        getAdditionalProperties(algorithm));

    final String network_service_banner =
        "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
    final List<JsonNode> collect = database.unsafeQuery(network_service_banner).toList();

    assertThat(collect.get(2).get("NETWORK_SERVICE_BANNER").asText(),
        equals("Oracle Advanced Security: " + algorithm + " encryption"));
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

    final JdbcDatabase database = Databases.createJdbcDatabase(clone.get("username").asText(),
        clone.get("password").asText(),
        String.format("jdbc:oracle:thin:@//%s:%s/%s",
            clone.get("host").asText(),
            clone.get("port").asText(),
            clone.get("sid").asText()),
        "oracle.jdbc.driver.OracleDriver",
        getAdditionalProperties(algorithm));

    final String network_service_banner = "SELECT sys_context('USERENV', 'NETWORK_PROTOCOL') as network_protocol FROM dual";
    final List<JsonNode> collect = database.unsafeQuery(network_service_banner).collect(Collectors.toList());

    assertEquals("tcp", collect.get(0).get("NETWORK_PROTOCOL").asText());
  }

}
