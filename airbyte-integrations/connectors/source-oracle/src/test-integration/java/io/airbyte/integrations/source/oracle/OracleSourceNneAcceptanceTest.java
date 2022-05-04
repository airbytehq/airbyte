/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.Test;

public class OracleSourceNneAcceptanceTest extends OracleSourceAcceptanceTest {

  @Test
  public void testEncrytion() throws SQLException {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("encryption", Jsons.jsonNode(ImmutableMap.builder()
        .put("encryption_method", "client_nne")
        .put("encryption_algorithm", "3DES168")
        .build()));

    final String algorithm = clone.get("encryption")
        .get("encryption_algorithm").asText();

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get("username").asText(),
            config.get("password").asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format("jdbc:oracle:thin:@//%s:%d/%s",
                clone.get("host").asText(),
                clone.get("port").asInt(),
                clone.get("sid").asText()),
            JdbcUtils.parseJdbcParameters("oracle.net.encryption_client=REQUIRED&" +
                "oracle.net.encryption_types_client=( "
                + algorithm + " )")
        )
    );

    final String networkServiceBanner =
        "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertTrue(collect.get(2).get("NETWORK_SERVICE_BANNER").asText().contains(algorithm + " Encryption"));
  }

  @Test
  public void testNoneEncrytion() throws SQLException {

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get("username").asText(),
            config.get("password").asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get("host").asText(),
                config.get("port").asInt(),
                config.get("sid").asText())
        )
    );

    final String networkServiceBanner =
        "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertTrue(collect.get(1).get("NETWORK_SERVICE_BANNER").asText().contains("Encryption service"));
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
            config.get("username").asText(),
            config.get("password").asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get("host").asText(),
                config.get("port").asInt(),
                config.get("sid").asText()),
            JdbcUtils.parseJdbcParameters("oracle.net.encryption_client=REQUIRED&" +
                "oracle.net.encryption_types_client=( "
                + algorithm + " )")
        ));

    final String networkServiceBanner = "SELECT sys_context('USERENV', 'NETWORK_PROTOCOL') as network_protocol FROM dual";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertEquals("tcp", collect.get(0).get("NETWORK_PROTOCOL").asText());
  }

}
