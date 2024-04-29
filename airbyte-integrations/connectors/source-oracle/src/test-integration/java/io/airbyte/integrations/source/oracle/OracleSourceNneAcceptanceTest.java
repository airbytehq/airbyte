/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import java.sql.SQLException;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

@Disabled
public class OracleSourceNneAcceptanceTest extends OracleSourceAcceptanceTest {

  private static final Duration CONNECTION_TIMEOUT = Duration.ofSeconds(60);

  @Test
  public void testEncrytion() throws SQLException {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put(JdbcUtils.ENCRYPTION_KEY, Jsons.jsonNode(ImmutableMap.builder()
        .put("encryption_method", "client_nne")
        .put("encryption_algorithm", "3DES168")
        .build()));

    final String algorithm = clone.get(JdbcUtils.ENCRYPTION_KEY)
        .get("encryption_algorithm").asText();

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format("jdbc:oracle:thin:@//%s:%d/%s",
                clone.get(JdbcUtils.HOST_KEY).asText(),
                clone.get(JdbcUtils.PORT_KEY).asInt(),
                clone.get("connection_data").get("service_name").asText()),
            JdbcUtils.parseJdbcParameters("oracle.net.encryption_client=REQUIRED&" +
                "oracle.net.encryption_types_client=( "
                + algorithm + " )"),
            CONNECTION_TIMEOUT));

    final String networkServiceBanner =
        "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertTrue(collect.get(2).get("NETWORK_SERVICE_BANNER").asText().contains(algorithm + " Encryption"));
  }

  @Test
  public void testNoneEncrytion() throws SQLException {

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get("connection_data").get("service_name").asText())));

    final String networkServiceBanner =
        "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertTrue(collect.get(1).get("NETWORK_SERVICE_BANNER").asText().contains("Encryption service"));
  }

  @Test
  public void testCheckProtocol() throws SQLException {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put(JdbcUtils.ENCRYPTION_KEY, Jsons.jsonNode(ImmutableMap.builder()
        .put("encryption_method", "client_nne")
        .put("encryption_algorithm", "AES256")
        .build()));

    final String algorithm = clone.get(JdbcUtils.ENCRYPTION_KEY)
        .get("encryption_algorithm").asText();

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get("connection_data").get("service_name").asText()),
            JdbcUtils.parseJdbcParameters("oracle.net.encryption_client=REQUIRED&" +
                "oracle.net.encryption_types_client=( "
                + algorithm + " )"),
            CONNECTION_TIMEOUT));

    final String networkServiceBanner = "SELECT sys_context('USERENV', 'NETWORK_PROTOCOL') as network_protocol FROM dual";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertEquals("tcp", collect.get(0).get("NETWORK_PROTOCOL").asText());
  }

}
