/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.adb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.sql.DataSource;
import java.util.Map;


public class AdbDestination extends AbstractJdbcDestination implements Destination {

    private static final Logger LOGGER = LoggerFactory.getLogger(AdbDestination.class);

    public static final String DRIVER_CLASS = DatabaseDriver.MYSQL.getDriverClassName();

    static final Map<String, String> DEFAULT_JDBC_PARAMETERS = ImmutableMap.of(
            // zero dates by default cannot be parsed into java date objects (they will throw an error)
            // in addition, users don't always have agency in fixing them e.g: maybe they don't own the database
            // and can't
            // remove zero date values.
            // since zero dates are placeholders, we convert them to null by default
            "zeroDateTimeBehavior", "convertToNull",
            "allowLoadLocalInfile", "true");

    public AdbDestination() {
        super(DRIVER_CLASS, new MySQLNameTransformer(), new MySQLSqlOperations());
    }

    @Override
    public AirbyteConnectionStatus check(JsonNode config) {
        final DataSource dataSource = getDataSource(config);
        try {
            final JdbcDatabase database = getDatabase(dataSource, config);
            final MySQLSqlOperations mySQLSqlOperations = (MySQLSqlOperations) getSqlOperations();

            final String outputSchema = getNamingResolver().getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
            attemptTableOperations(outputSchema, database, getNamingResolver(), mySQLSqlOperations, false);

//      mySQLSqlOperations.verifyLocalFileEnabled(database);

            final MySQLSqlOperations.VersionCompatibility compatibility = mySQLSqlOperations.isCompatibleVersion(database);
            if (!compatibility.isCompatible()) {
                throw new RuntimeException(String
                        .format("Your MySQL version %s is not compatible with Airbyte",
                                compatibility.getVersion()));
            }

            return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
        } catch (final ConnectionErrorException e) {
            final String message = ErrorMessage.getErrorMessage(e.getStateCode(), e.getErrorCode(), e.getExceptionMessage(), e);
            AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message);
            return new AirbyteConnectionStatus()
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
                    .withMessage(message);
        } catch (final Exception e) {
            LOGGER.error("Exception while checking connection: ", e);
            return new AirbyteConnectionStatus()
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
                    .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
        } finally {
            try {
                DataSourceFactory.close(dataSource);
            } catch (final Exception e) {
                LOGGER.warn("Unable to close data source.", e);
            }
        }
    }

    @Override
    protected Map<String, String> getDefaultConnectionProperties(JsonNode config) {
        return DEFAULT_JDBC_PARAMETERS;
    }

    @Override
    public JsonNode toJdbcConfig(JsonNode config) {
        final String jdbcUrl = String.format("jdbc:mysql://%s:%s/%s",
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asText(),
                config.get(JdbcUtils.DATABASE_KEY).asText());

        final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
                .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
                .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);

        if (config.has(JdbcUtils.PASSWORD_KEY)) {
            configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
        }
        if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
            configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
        }
        if (!config.has("wm_tenant_id")) {
            throw new RuntimeException("wm_tenant_id is required");
        }
        configBuilder.put("wm_tenant_id", config.get("wm_tenant_id").asText());

        return Jsons.jsonNode(configBuilder.build());
    }

    @Override
    protected JdbcSqlGenerator getSqlGenerator() {
        throw new UnsupportedOperationException("mysql does not yet support DV2");
    }

    public static void main(final String[] args) throws Exception {
        final Destination destination = new AdbDestination();
        LOGGER.info("starting destination: {}", AdbDestination.class);
        new IntegrationRunner(destination).run(args);
        LOGGER.info("completed destination: {}", AdbDestination.class);
    }


}
