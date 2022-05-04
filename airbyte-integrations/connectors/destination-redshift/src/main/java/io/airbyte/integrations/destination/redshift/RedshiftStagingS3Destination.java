package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import io.airbyte.integrations.destination.s3.S3Destination;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.function.Consumer;

import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.SSL_JDBC_PARAMETERS;
import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.getJdbcDatabase;
import static io.airbyte.integrations.destination.s3.S3DestinationConfig.getS3DestinationConfig;


public class RedshiftStagingS3Destination extends AbstractJdbcDestination implements Destination {

    private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStagingS3Destination.class);
    private final RedshiftDataTmpTableMode redshiftDataTmpTableMode;

    public RedshiftStagingS3Destination(RedshiftDataTmpTableMode redshiftDataTmpTableMode) {
        super(RedshiftInsertDestination.DRIVER_CLASS, new RedshiftSQLNameTransformer(), new RedshiftSqlOperations(redshiftDataTmpTableMode));
        this.redshiftDataTmpTableMode=redshiftDataTmpTableMode;
    }
    @Override
    public AirbyteConnectionStatus check(final JsonNode config) {
        final S3DestinationConfig s3Config = getS3DestinationConfig(config);
        S3Destination.attemptS3WriteAndDelete(new S3StorageOperations(new RedshiftSQLNameTransformer(), s3Config.getS3Client(), s3Config), s3Config, "");


        final NamingConventionTransformer nameTransformer = getNamingResolver();
        final RedshiftS3StagingSqlOperations redshiftS3StagingSqlOperations =
                new RedshiftS3StagingSqlOperations(nameTransformer, s3Config.getS3Client(), s3Config, redshiftDataTmpTableMode);
        try (final JdbcDatabase database = getDatabase(config)) {
            final String outputSchema = super.getNamingResolver().getIdentifier(config.get("schema").asText());
            AirbyteSentry.executeWithTracing("CreateAndDropTable",
                    () -> attemptSQLCreateAndDropTableOperations(outputSchema, database, nameTransformer, redshiftS3StagingSqlOperations));
            return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
        } catch (final Exception e) {
            LOGGER.error("Exception while checking connection: ", e);
            return new AirbyteConnectionStatus()
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
                    .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
        }

    }
    @Override
    protected JdbcDatabase getDatabase(final JsonNode config) {
        return getJdbcDatabase(config);
    }
    @Override
    protected NamingConventionTransformer getNamingResolver() {
        return new RedshiftSQLNameTransformer();
    }

    @Override
    protected Map<String, String> getDefaultConnectionProperties(JsonNode config) {
        return SSL_JDBC_PARAMETERS;
    }

//TODO ?????????????
    // this is a no op since we override getDatabase.

    @Override
    public JsonNode toJdbcConfig(JsonNode config) {
        return Jsons.emptyObject();
    }

    @Override
    public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                              final ConfiguredAirbyteCatalog catalog,
                                              final Consumer<AirbyteMessage> outputRecordCollector) {
        final S3DestinationConfig s3Config = getS3DestinationConfig(config);
        return new StagingConsumerFactory().create(
                outputRecordCollector,
                getDatabase(config),
                new RedshiftS3StagingSqlOperations(getNamingResolver(), s3Config.getS3Client(), s3Config, redshiftDataTmpTableMode),
                getNamingResolver(),
                CsvSerializedBuffer.createFunction(null, () -> new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX)),
                config,
                catalog);
    }
}
