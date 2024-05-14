/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDestinationHandler;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftRawTableAirbyteMetaMigration;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftState;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSuperLimitationTransformer;
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil;
import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import javax.sql.DataSource;

public class RedshiftInsertDestination extends AbstractJdbcDestination<RedshiftState> {

  public static final String DRIVER_CLASS = DatabaseDriver.REDSHIFT.getDriverClassName();
  public static final Map<String, String> SSL_JDBC_PARAMETERS = ImmutableMap.of(
      JdbcUtils.SSL_KEY, "true",
      "sslfactory", "com.amazon.redshift.ssl.NonValidatingFactory");

  // insert into stmt has ~200 bytes
  // Per record overhead of ~150 bytes for strings in statement like JSON_PARSE.. uuid etc
  // If the flush size allows the max batch of 10k records, then net overhead is ~1.5MB.
  // Lets round it to 2MB for wiggle room and keep a max buffer of 14MB per flush.
  // This will allow not sending record set larger than 14M limiting the batch insert statement.
  private static final Long REDSHIFT_OPTIMAL_BATCH_SIZE_FOR_FLUSH = 14 * 1024 * 1024L;

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new RedshiftInsertDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public RedshiftInsertDestination() {
    super(DRIVER_CLASS, REDSHIFT_OPTIMAL_BATCH_SIZE_FOR_FLUSH, new RedshiftSQLNameTransformer(), new RedshiftSqlOperations());
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode redshiftConfig) {
    return getJdbcConfig(redshiftConfig);
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    final var jdbcConfig = getJdbcConfig(config);
    return DataSourceFactory.create(
        jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        RedshiftInsertDestination.DRIVER_CLASS,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        getDefaultConnectionProperties(config),
        Duration.ofMinutes(2));
  }

  @Override
  protected void destinationSpecificTableOperations(final JdbcDatabase database) throws Exception {
    RedshiftUtil.checkSvvTableAccess(database);
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  public JdbcDatabase getDatabase(final DataSource dataSource, final JdbcSourceOperations sourceOperations) {
    return new DefaultJdbcDatabase(dataSource, sourceOperations);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    // The following properties can be overriden through jdbcUrlParameters in the config.
    final Map<String, String> connectionOptions = new HashMap<>();
    // Redshift properties
    // https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-configuration-options.html#jdbc20-connecttimeout-option
    // connectTimeout is different from Hikari pool's connectionTimout, driver defaults to 10seconds so
    // increase it to match hikari's default
    connectionOptions.put("connectTimeout", "120");
    // See RedshiftProperty.LOG_SERVER_ERROR_DETAIL, defaults to true
    connectionOptions.put("logservererrordetail", "false");
    // HikariPool properties
    // https://github.com/brettwooldridge/HikariCP?tab=readme-ov-file#frequently-used
    // TODO: Change data source factory to configure these properties
    connectionOptions.putAll(SSL_JDBC_PARAMETERS);
    return connectionOptions;
  }

  public static JsonNode getJdbcConfig(final JsonNode redshiftConfig) {
    final String schema = Optional.ofNullable(redshiftConfig.get(JdbcUtils.SCHEMA_KEY)).map(JsonNode::asText).orElse("public");
    final Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, redshiftConfig.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.PASSWORD_KEY, redshiftConfig.get(JdbcUtils.PASSWORD_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, String.format("jdbc:redshift://%s:%s/%s",
            redshiftConfig.get(JdbcUtils.HOST_KEY).asText(),
            redshiftConfig.get(JdbcUtils.PORT_KEY).asText(),
            redshiftConfig.get(JdbcUtils.DATABASE_KEY).asText()))
        .put(JdbcUtils.SCHEMA_KEY, schema);

    if (redshiftConfig.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, redshiftConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  protected JdbcSqlGenerator getSqlGenerator(final JsonNode config) {
    return new RedshiftSqlGenerator(super.getNamingResolver(), config);
  }

  @Override
  protected JdbcDestinationHandler<RedshiftState> getDestinationHandler(final String databaseName,
                                                                        final JdbcDatabase database,
                                                                        String rawTableSchema) {
    return new RedshiftDestinationHandler(databaseName, database, rawTableSchema);
  }

  @Override
  protected List<Migration<RedshiftState>> getMigrations(JdbcDatabase database,
                                                         String databaseName,
                                                         SqlGenerator sqlGenerator,
                                                         DestinationHandler<RedshiftState> destinationHandler) {
    return List.of(new RedshiftRawTableAirbyteMetaMigration(database, databaseName));
  }

  @Override
  protected StreamAwareDataTransformer getDataTransformer(ParsedCatalog parsedCatalog, String defaultNamespace) {
    return new RedshiftSuperLimitationTransformer(parsedCatalog, defaultNamespace);
  }

}
