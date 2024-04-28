/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yellowbrick;

import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.DISABLE;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.PARAM_MODE;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.PARAM_SSL;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.PARAM_SSL_MODE;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.obtainConnectionOptions;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.*;
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
import io.airbyte.integrations.destination.yellowbrick.typing_deduping.YellowbrickDataTransformer;
import io.airbyte.integrations.destination.yellowbrick.typing_deduping.YellowbrickDestinationHandler;
import io.airbyte.integrations.destination.yellowbrick.typing_deduping.YellowbrickSqlGenerator;
import io.airbyte.integrations.destination.yellowbrick.typing_deduping.YellowbrickState;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class YellowbrickDestination extends AbstractJdbcDestination<YellowbrickState> implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(YellowbrickDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new YellowbrickDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public YellowbrickDestination() {
    super(DRIVER_CLASS, new YellowbrickSQLNameTransformer(), new YellowbrickSqlOperations());
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    final Map<String, String> additionalParameters = new HashMap<>();
    if (!config.has(PARAM_SSL) || config.get(PARAM_SSL).asBoolean()) {
      if (config.has(PARAM_SSL_MODE)) {
        if (DISABLE.equals(config.get(PARAM_SSL_MODE).get(PARAM_MODE).asText())) {
          additionalParameters.put("sslmode", DISABLE);
        } else {
          additionalParameters.putAll(obtainConnectionOptions(config.get(PARAM_SSL_MODE)));
        }
      } else {
        additionalParameters.put(JdbcUtils.SSL_KEY, "true");
        additionalParameters.put("sslmode", "require");
      }
    }
    return additionalParameters;
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String schema = Optional.ofNullable(config.get(JdbcUtils.SCHEMA_KEY)).map(JsonNode::asText).orElse("public");

    String encodedDatabase = config.get(JdbcUtils.DATABASE_KEY).asText();
    if (encodedDatabase != null) {
      try {
        encodedDatabase = URLEncoder.encode(encodedDatabase, "UTF-8");
      } catch (final UnsupportedEncodingException e) {
        // Should never happen
        e.printStackTrace();
      }
    }
    final String jdbcUrl = String.format("jdbc:postgresql://%s:%s/%s?",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        encodedDatabase);

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)
        .put(JdbcUtils.SCHEMA_KEY, schema);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  protected JdbcDestinationHandler<YellowbrickState> getDestinationHandler(String databaseName, JdbcDatabase database, String rawTableSchema) {
    return new YellowbrickDestinationHandler(databaseName, database, rawTableSchema);
  }

  @Override
  protected JdbcSqlGenerator getSqlGenerator() {
    return new YellowbrickSqlGenerator(new YellowbrickSQLNameTransformer());
  }

  @Override
  protected StreamAwareDataTransformer getDataTransformer(ParsedCatalog parsedCatalog, String defaultNamespace) {
    return new YellowbrickDataTransformer();
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }

  @Override
  protected List<Migration<YellowbrickState>> getMigrations(JdbcDatabase database,
                                                            String databaseName,
                                                            SqlGenerator sqlGenerator,
                                                            DestinationHandler<YellowbrickState> destinationHandler) {
    return List.of();
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = YellowbrickDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", YellowbrickDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", YellowbrickDestination.class);
  }

}
