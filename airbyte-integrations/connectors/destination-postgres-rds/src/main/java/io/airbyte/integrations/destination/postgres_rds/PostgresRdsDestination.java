/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres_rds;

import static io.airbyte.integrations.util.PostgresSslConnectionUtils.DISABLE;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.PARAM_MODE;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.PARAM_SSL;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.PARAM_SSL_MODE;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.obtainConnectionOptions;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.rds.auth.GetIamAuthTokenRequest;
import com.amazonaws.services.rds.auth.RdsIamAuthTokenGenerator;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.postgres.PostgresSQLNameTransformer;
import io.airbyte.integrations.destination.postgres.PostgresSqlOperations;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresRdsDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresRdsDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();

  public static final String CREDENTIALS_KEY = "credentials";
  public static final String ACCESS_KEY_ID_KEY = "access_key_id";
  public static final String SECRET_ACCESS_KEY_KEY = "secret_access_key";
  public static final String RDS_REGION_KEY = "rds_region";

  public static void main(final String[] args) throws Exception {
    final Destination destination = new SshWrappedDestination(new PostgresRdsDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
    LOGGER.info("starting destination: Postgres RDS for {}", PostgresRdsDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: Postgres RDS for {}", PostgresRdsDestination.class);
  }

  public PostgresRdsDestination() {
    super(DRIVER_CLASS, new PostgresSQLNameTransformer(), new PostgresSqlOperations());
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
  public JsonNode toJdbcConfig(JsonNode config) {
    final String schema = Optional.ofNullable(config.get(JdbcUtils.SCHEMA_KEY)).map(JsonNode::asText).orElse("public");

    String encodedDatabase = config.get(JdbcUtils.DATABASE_KEY).asText();
    if (encodedDatabase != null) {
      encodedDatabase = URLEncoder.encode(encodedDatabase, StandardCharsets.UTF_8);
    }
    final String jdbcUrl = String.format("jdbc:postgresql://%s:%s/%s?",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        encodedDatabase);

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)
        .put(JdbcUtils.SCHEMA_KEY, schema);

    if (config.has(CREDENTIALS_KEY)) {
      final JsonNode credentials = config.get(CREDENTIALS_KEY);
      if (credentials.has(JdbcUtils.PASSWORD_KEY)) {
        configBuilder.put(JdbcUtils.PASSWORD_KEY, credentials.get(JdbcUtils.PASSWORD_KEY).asText());
      } else {
        String accessKeyId = credentials.get(ACCESS_KEY_ID_KEY).asText();
        String secretKey = credentials.get(SECRET_ACCESS_KEY_KEY).asText();
        String rdsRegion = credentials.get(RDS_REGION_KEY).asText();

        BasicAWSCredentials awsCredentials = new BasicAWSCredentials(accessKeyId, secretKey);

        RdsIamAuthTokenGenerator generator = RdsIamAuthTokenGenerator.builder()
            .credentials(new AWSStaticCredentialsProvider(awsCredentials)).region(rdsRegion).build();
        String password = generator.getAuthToken(GetIamAuthTokenRequest.builder()
            .hostname(config.get(JdbcUtils.HOST_KEY).asText())
            .port(config.get(JdbcUtils.PORT_KEY).asInt())
            .userName(config.get(JdbcUtils.USERNAME_KEY).asText()).build());

        configBuilder.put(JdbcUtils.PASSWORD_KEY, password);
      }
    }


    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

}
