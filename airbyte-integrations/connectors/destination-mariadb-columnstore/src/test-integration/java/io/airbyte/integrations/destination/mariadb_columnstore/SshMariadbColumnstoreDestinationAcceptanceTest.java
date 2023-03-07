/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MariaDBContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.utility.DockerImageName;

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshMariadbColumnstoreDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(MariadbColumnstoreDestinationAcceptanceTest.class);
  private static final Network network = Network.newNetwork();

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
    if (config.get(JdbcUtils.DATABASE_KEY) == null) {
      return null;
    }
    return config.get(JdbcUtils.DATABASE_KEY).asText();
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
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
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
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
    final DSLContext dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MARIADB.getDriverClassName(),
        String.format(DatabaseDriver.MARIADB.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.MARIADB);
    return new Database(dslContext);
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
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    bastion.initAndStartBastion(network);
    startAndInitJdbcContainer();
  }

  private void startAndInitJdbcContainer() throws Exception {
    final DockerImageName mcsImage = DockerImageName.parse("fengdi/columnstore:1.5.2").asCompatibleSubstituteFor("mariadb");
    db = new MariaDBContainer<>(mcsImage)
        .withNetwork(network);
    db.start();

    final String createUser = String.format("CREATE USER '%s'@'%%' IDENTIFIED BY '%s';", db.getUsername(), db.getPassword());
    final String grantAll = String.format("GRANT ALL PRIVILEGES ON *.* TO '%s'@'%%' IDENTIFIED BY '%s';", db.getUsername(), db.getPassword());
    final String createDb = String.format("CREATE DATABASE %s DEFAULT CHARSET = utf8;", db.getDatabaseName());
    db.execInContainer("mariadb", "-e", createUser + grantAll + createDb);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bastion.stopAndCloseContainers(db);
  }

}
