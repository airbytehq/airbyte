/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Disabled;
import org.testcontainers.containers.ClickHouseContainer;

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshClickhouseDestinationAcceptanceTest extends DestinationAcceptanceTest {

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  private static final String DB_NAME = "default";

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private ClickHouseContainer db;
  private final SshBastionContainer bastion = new SshBastionContainer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-clickhouse:dev";
  }

  @Override
  protected boolean supportsNormalization() {
    return true;
  }

  @Override
  protected boolean supportsDBT() {
    return false;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get("database") == null) {
      return null;
    }
    return config.get("database").asText();
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), bastion.getBasicDbConfigBuider(db, DB_NAME)
        .put("schema", DB_NAME));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv,
                                                     final String streamName,
                                                     final String namespace)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getIdentifier(streamName), namespace);
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    return SshTunnel.sshWrap(
        getConfig(),
        ClickhouseDestination.HOST_KEY,
        ClickhouseDestination.PORT_KEY,
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabase(mangledConfig)
            .query(String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
            .collect(Collectors.toList()));
  }

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
      result.add(resolved.toUpperCase());
    }
    return result;
  }

  private static JdbcDatabase getDatabase(final JsonNode config) {
    return Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.has("password") ? config.get("password").asText() : null,
        String.format("jdbc:clickhouse://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        ClickhouseDestination.DRIVER_CLASS);
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    bastion.initAndStartBastion();
    db = (ClickHouseContainer) new ClickHouseContainer("yandex/clickhouse-server").withNetwork(bastion.getNetWork());
    db.start();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    bastion.stopAndCloseContainers(db);
  }

  /**
   * The SQL script generated by old version of dbt in 'test' step isn't compatible with ClickHouse,
   * so we skip this test for now.
   *
   * Ref: https://github.com/dbt-labs/dbt-core/issues/3905
   *
   * @throws Exception
   */
  @Disabled
  public void testCustomDbtTransformations() throws Exception {
    super.testCustomDbtTransformations();
  }

  @Disabled
  public void testCustomDbtTransformationsFailure() throws Exception {}

  /**
   * The normalization container needs native port, while destination container needs HTTP port, we
   * can't inject the port switch statement into DestinationAcceptanceTest.runSync() method for this
   * test, so we skip it.
   *
   * @throws Exception
   */
  @Disabled
  public void testIncrementalDedupeSync() throws Exception {
    super.testIncrementalDedupeSync();
  }

  /**
   * The normalization container needs native port, while destination container needs HTTP port, we
   * can't inject the port switch statement into DestinationAcceptanceTest.runSync() method for this
   * test, so we skip it.
   *
   * @throws Exception
   */
  @Disabled
  public void testSyncWithNormalization(final String messagesFilename, final String catalogFilename) throws Exception {
    super.testSyncWithNormalization(messagesFilename, catalogFilename);
  }

}
