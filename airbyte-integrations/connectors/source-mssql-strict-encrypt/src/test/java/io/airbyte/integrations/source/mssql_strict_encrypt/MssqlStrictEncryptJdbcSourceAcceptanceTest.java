/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql_strict_encrypt;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.mssql.MsSQLContainerFactory;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class MssqlStrictEncryptJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<MssqlSourceStrictEncrypt, MsSQLTestDatabase> {

  static {
    // In mssql, timestamp is generated automatically, so we need to use
    // the datetime type instead so that we can set the value manually.
    COL_TIMESTAMP_TYPE = "DATETIME";
  }

  @Override
  protected void maybeSetShorterConnectionTimeout(final JsonNode config) {
    ((ObjectNode) config).put(JdbcUtils.JDBC_URL_PARAMS_KEY, "loginTimeout=1");
  }

  protected JsonNode config() {
    return testdb.testConfigBuilder()
        .withSsl(Map.of("ssl_method", "encrypted_trust_server_certificate"))
        .build();
  }

  @Override
  protected MssqlSourceStrictEncrypt source() {
    return new MssqlSourceStrictEncrypt();
  }

  @Override
  protected MsSQLTestDatabase createTestDatabase() {
    final var container = new MsSQLContainerFactory().shared("mcr.microsoft.com/mssql/server:2022-RTM-CU2-ubuntu-20.04");
    final var testdb = new MsSQLTestDatabase(container);
    return testdb
        .withConnectionProperty("encrypt", "true")
        .withConnectionProperty("trustServerCertificate", "true")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .initialized();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source().spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class));

    assertEquals(expected, actual);
  }

  @Override
  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

}
