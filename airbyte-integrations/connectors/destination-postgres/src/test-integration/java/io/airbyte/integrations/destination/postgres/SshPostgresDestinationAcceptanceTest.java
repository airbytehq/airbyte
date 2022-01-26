/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE;
import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE_TIME;

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
import io.airbyte.integrations.standardtest.destination.DateTimeUtils;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.TimeZone;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.RandomStringUtils;
import org.testcontainers.containers.PostgreSQLContainer;

// todo (cgardens) - likely some of this could be further de-duplicated with
// PostgresDestinationAcceptanceTest.

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshPostgresDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();
  private static final String schemaName = RandomStringUtils.randomAlphabetic(8).toLowerCase();
  private static PostgreSQLContainer<?> db;
  private final SshBastionContainer bastion = new SshBastionContainer();

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), bastion.getBasicDbConfigBuider(db).put("schema", schemaName));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean supportsNormalization() {
    return true;
  }

  @Override
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    // Temporarily disabling the behavior of the ExtendedNameTransformer, see (issue #1785) so we don't
    // use quoted names
    // if (!tableName.startsWith("\"")) {
    // // Currently, Normalization always quote tables identifiers
    // //tableName = "\"" + tableName + "\"";
    // }
    return retrieveRecordsFromTable(tableName, namespace);
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

  private static Database getDatabaseFromConfig(final JsonNode config) {
    return Databases.createPostgresDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s", config.get("host").asText(), config.get("port").asText(),
            config.get("database").asText()));
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    TimeZone.setDefault(TimeZone.getTimeZone("UTC"));
    final JsonNode config = getConfig();
    return SshTunnel.sshWrap(
        config,
        PostgresDestination.HOST_KEY,
        PostgresDestination.PORT_KEY,
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(
                ctx -> ctx
                    .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                    .stream()
                    .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                    .map(Jsons::deserialize)
                    .collect(Collectors.toList())));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {

    startTestContainers();
    // do everything in a randomly generated schema so that we can wipe it out at the end.
    SshTunnel.sshWrap(
        getConfig(),
        PostgresDestination.HOST_KEY,
        PostgresDestination.PORT_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> ctx.fetch(String.format("CREATE SCHEMA %s;", schemaName)));
        });
  }

  private void startTestContainers() {
    bastion.initAndStartBastion();
    initAndStartJdbcContainer();
  }

  private void initAndStartJdbcContainer() {
    db = new PostgreSQLContainer<>("postgres:13-alpine")
        .withNetwork(bastion.getNetWork());
    db.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    // blow away the test schema at the end.
    SshTunnel.sshWrap(
        getConfig(),
        PostgresDestination.HOST_KEY,
        PostgresDestination.PORT_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> ctx.fetch(String.format("DROP SCHEMA %s CASCADE;", schemaName)));
        });

    bastion.stopAndCloseContainers(db);
  }

  @Override
  public boolean requiresDateTimeConversionForNormalizedSync() {
    return true;
  }

  @Override
  public void convertDateTime(ObjectNode data, Map<String, String> dateTimeFieldNames) {
    var fields = StreamSupport.stream(Spliterators.spliteratorUnknownSize(data.fields(),
        Spliterator.ORDERED), false).toList();
    data.removeAll();
    fields.forEach(field -> {
      var key = field.getKey();
      if (dateTimeFieldNames.containsKey(key)) {
        switch (dateTimeFieldNames.get(key)) {
          case DATE_TIME -> data.put(key.toLowerCase(), DateTimeUtils.convertToPostgresFormat(field.getValue().asText()));
          case DATE -> data.put(key.toLowerCase(), DateTimeUtils.convertToDateFormat(field.getValue().asText()));
        }
      } else {
        data.set(key.toLowerCase(), field.getValue());
      }
    });
  }


}
