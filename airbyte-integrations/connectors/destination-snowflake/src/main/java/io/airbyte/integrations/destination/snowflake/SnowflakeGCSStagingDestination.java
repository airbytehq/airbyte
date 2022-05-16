package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.storage.CloudStorageConfigs;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
//import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;

public class SnowflakeGCSStagingDestination extends AbstractJdbcDestination implements Destination {

    private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeGCSStagingDestination.class);

    public SnowflakeGCSStagingDestination() {
        this(new SnowflakeSQLNameTransformer());
    }

    public SnowflakeGCSStagingDestination(final SnowflakeSQLNameTransformer nameTransformer) {
        super("", nameTransformer, new SnowflakeSqlOperations());
    }

    @Override
    public AirbyteConnectionStatus check(final JsonNode config) {
        CloudStorageConfigs.GcsConfig vs;
//        GcsDestination fdb;
        S3DestinationConfig jghs;

        final GcsDestinationConfig destinationConfig = GcsDestinationConfig.getGcsDestinationConfig(config);
//
////        final S3DestinationConfig s3Config = getS3DestinationConfig(config);
//        final NamingConventionTransformer nameTransformer = getNamingResolver();
//        final SnowflakeS3StagingSqlOperations snowflakeS3StagingSqlOperations =
//                new SnowflakeS3StagingSqlOperations(nameTransformer, s3Config.getS3Client(), s3Config, encryptionConfig);
//        try (final JdbcDatabase database = getDatabase(config)) {
//            final String outputSchema = super.getNamingResolver().getIdentifier(config.get("schema").asText());
//            AirbyteSentry.executeWithTracing("CreateAndDropTable",
//                    () -> attemptSQLCreateAndDropTableOperations(outputSchema, database, nameTransformer, snowflakeS3StagingSqlOperations));
//            AirbyteSentry.executeWithTracing("CreateAndDropStage",
//                    () -> attemptSQLCreateAndDropStages(outputSchema, database, nameTransformer, snowflakeS3StagingSqlOperations));
            return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
//        } catch (final Exception e) {
//            LOGGER.error("Exception while checking connection: ", e);
//            return new AirbyteConnectionStatus()
//                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
//                    .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
//        }
    }
    @Override
    protected Map<String, String> getDefaultConnectionProperties(JsonNode config) {
        return null;
    }

    @Override
    public JsonNode toJdbcConfig(JsonNode config) {
        return null;
    }
}
