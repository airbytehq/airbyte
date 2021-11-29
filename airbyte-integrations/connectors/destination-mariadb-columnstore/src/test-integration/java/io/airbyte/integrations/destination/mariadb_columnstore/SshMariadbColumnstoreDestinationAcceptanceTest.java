/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MariaDBContainer;
import org.testcontainers.utility.DockerImageName;

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshMariadbColumnstoreDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(MariadbColumnstoreDestinationAcceptanceTest.class);

  private final ExtendedNameTransformer namingResolver = new MariadbColumnstoreNameTransformer();

  private JsonNode configJson;

  private MariaDBContainer<?> db;

  private final SshBastionContainer bastion = new SshBastionContainer();

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-mariadb-columnstore:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), bastion.getBasicDbConfigBuider(db));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get("database") == null) {
      return null;
    }
    return config.get("database").asText();
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
    final JsonNode config = getConfig();
    return SshTunnel.sshWrap(
        config,
        MariadbColumnstoreDestination.HOST_KEY,
        MariadbColumnstoreDestination.PORT_KEY,
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(
                ctx -> ctx
                    .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                    .stream()
                    .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                    .map(Jsons::deserialize)
                    .collect(Collectors.toList())));
  }

  private static Database getDatabaseFromConfig(final JsonNode config) {
    return Databases.createMariaDbDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:mariadb://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()));
  }

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);

    return result;
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    bastion.initAndStartBastion();
    startAndInitJdbcContainer();
  }

  private void startAndInitJdbcContainer() throws Exception {
    DockerImageName mcsImage = DockerImageName.parse("mariadb/columnstore").asCompatibleSubstituteFor("mariadb");
    db = new MariaDBContainer<>(mcsImage)
        .withNetwork(bastion.getNetWork());
    db.start();

    String createUser = String.format("CREATE USER '%s'@'%%' IDENTIFIED BY '%s';", db.getUsername(), db.getPassword());
    String grantAll = String.format("GRANT ALL PRIVILEGES ON *.* TO '%s'@'%%' IDENTIFIED BY '%s';", db.getUsername(), db.getPassword());
    String createDb = String.format("CREATE DATABASE %s DEFAULT CHARSET = utf8;", db.getDatabaseName());
    db.execInContainer("mariadb", "-e", createUser + grantAll + createDb);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    bastion.stopAndCloseContainers(db);
  }

}
