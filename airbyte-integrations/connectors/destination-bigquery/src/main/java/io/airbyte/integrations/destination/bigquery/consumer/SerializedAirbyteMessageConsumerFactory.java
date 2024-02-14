package io.airbyte.integrations.destination.bigquery.consumer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.TableId;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.config.AirbyteConfiguredCatalog;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.bigquery.BigQueryGcsOperations;
import io.airbyte.integrations.destination.bigquery.BigQueryRecordStandardConsumer;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.integrations.destination.bigquery.BigQueryStagingConsumerFactory;
import io.airbyte.integrations.destination.bigquery.BigQueryStagingOperations;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.UploadingMethod;
import io.airbyte.integrations.destination.bigquery.config.properties.BigQueryConnectorConfiguration;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsCsvBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryV1V2Migrator;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryV2TableMigrator;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryUploaderFactory;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.cdk.integrations.destination.gcs.GcsNameTransformer;
import io.airbyte.cdk.integrations.destination.gcs.GcsStorageOperations;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import org.apache.commons.lang3.StringUtils;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;

@Singleton
public class SerializedAirbyteMessageConsumerFactory {

    private static final Logger LOGGER = LoggerFactory.getLogger(SerializedAirbyteMessageConsumerFactory.class);

    private final BigQuery bigQuery;
    private final BigQueryConnectorConfiguration configuration;
    private final BigQuerySqlGenerator sqlGenerator;
    private final BigQuerySQLNameTransformer namingResolver;
    private final BigQueryUtils bigQueryUtils;
    private final BigQueryV1V2Migrator bigQueryV1V2Migrator;
    private final BigQueryV2TableMigrator v2RawTableMigrator;
    private final Consumer<AirbyteMessage> outputRecordCollector;
    private final CatalogParser catalogParser;
    private final BigQueryDestinationHandler destinationHandler;

    private final TyperDeduper typerDeduper;

    public SerializedAirbyteMessageConsumerFactory(final AirbyteConfiguredCatalog airbyteConfiguredCatalog,
                                                   final BigQuery bigQuery,
                                                   final BigQueryConnectorConfiguration configuration,
                                                   final BigQuerySqlGenerator sqlGenerator,
                                                   final BigQuerySQLNameTransformer namingResolver,
                                                   final BigQueryUtils bigQueryUtils,
                                                   final BigQueryV1V2Migrator bigQueryV1V2Migrator,
                                                   final BigQueryV2TableMigrator v2RawTableMigrator,
                                                   final BigQueryDestinationHandler destinationHandler,
                                                   @Named("outputRecordCollector") final Consumer<AirbyteMessage> outputRecordCollector) {
        this.bigQuery = bigQuery;
        this.catalogParser = new CatalogParser(sqlGenerator);   //TODO convert to Singleton
        this.configuration = configuration;
        this.bigQueryUtils = bigQueryUtils;
        this.bigQueryV1V2Migrator = bigQueryV1V2Migrator;
        this.namingResolver = namingResolver;
        this.outputRecordCollector = outputRecordCollector;
        this.sqlGenerator = sqlGenerator;
        this.v2RawTableMigrator = v2RawTableMigrator;
        this.destinationHandler = destinationHandler;
        this.typerDeduper = buildTyperDeduper(sqlGenerator, catalogParser.parseCatalog(airbyteConfiguredCatalog.getConfiguredCatalog()), bigQuery, configuration);
    }

    public SerializedAirbyteMessageConsumer createMessageConsumer(final ConfiguredAirbyteCatalog catalog) throws Exception {
        final UploadingMethod uploadingMethod = bigQueryUtils.getLoadingMethod(configuration);
        final String defaultNamespace = bigQueryUtils.getDatasetId(configuration);
        setDefaultStreamNamespace(catalog, defaultNamespace);
        final ParsedCatalog parsedCatalog = parseCatalog(catalog);

        AirbyteExceptionHandler.addAllStringsInConfigForDeinterpolation(configuration.toJson());
        if (StringUtils.isNotBlank(configuration.getCredentialsJson()) && configuration.getLoadingMethod().getCredential() != null) {
            // If the service account key is a non-null string, we will try to
            // deserialize it. Otherwise, we will let the Google library find it in
            // the environment during the client initialization.
            if (StringUtils.isNotBlank(configuration.getCredentialsJson())) {
                // There are cases where we fail to deserialize the service account key. In these cases, we
                // shouldn't do anything.
                // Google's creds library is more lenient with JSON-parsing than Jackson, and I'd rather just let it
                // go.
                Jsons.tryDeserialize(configuration.getCredentialsJson())
                        .ifPresent(AirbyteExceptionHandler::addAllStringsInConfigForDeinterpolation);
            } else {
                AirbyteExceptionHandler.addAllStringsInConfigForDeinterpolation(Jsons.jsonNode(configuration.getLoadingMethod().getCredential()));
            }
        }

        if (uploadingMethod == UploadingMethod.STANDARD) {
            LOGGER.warn("The \"standard\" upload mode is not performant, and is not recommended for production. " +
                    "Please use the GCS upload mode if you are syncing a large amount of data.");
            return getStandardRecordConsumer(bigQuery, configuration, catalog, parsedCatalog, outputRecordCollector);
        }

        final StandardNameTransformer gcsNameTransformer = new GcsNameTransformer();
        final GcsDestinationConfig gcsConfig = bigQueryUtils.getGcsCsvDestinationConfig(configuration);
        final UUID stagingId = UUID.randomUUID();
        final DateTime syncDatetime = DateTime.now(DateTimeZone.UTC);
        final boolean keepStagingFiles = bigQueryUtils.isKeepFilesInGcs(configuration);
        final GcsStorageOperations gcsOperations = new GcsStorageOperations(gcsNameTransformer, gcsConfig.getS3Client(), gcsConfig);
        final BigQueryStagingOperations bigQueryGcsOperations = new BigQueryGcsOperations(
                bigQuery,
                bigQueryUtils,
                gcsNameTransformer,
                gcsConfig,
                gcsOperations,
                stagingId,
                syncDatetime,
                keepStagingFiles);

        return new BigQueryStagingConsumerFactory().createAsync(
                configuration,
                catalog,
                outputRecordCollector,
                bigQueryGcsOperations,
                bigQueryUtils,
                getCsvRecordFormatterCreator(namingResolver),
                namingResolver::getTmpTableName,
                typerDeduper,
                parsedCatalog,
                bigQueryUtils.getDatasetId(configuration));
    }

    private void setDefaultStreamNamespace(final ConfiguredAirbyteCatalog catalog, final String namespace) {
        // Set the default namespace on streams with null namespace. This means we don't need to repeat this
        // logic in the rest of the connector.
        // (record messages still need to handle null namespaces though, which currently happens in e.g.
        // AsyncStreamConsumer#accept)
        // This probably should be shared logic amongst destinations eventually.
        for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
            if (StringUtils.isEmpty(stream.getStream().getNamespace())) {
                stream.getStream().withNamespace(namespace);
            }
        }
    }

    protected Function<JsonNode, BigQueryRecordFormatter> getCsvRecordFormatterCreator(final BigQuerySQLNameTransformer namingResolver) {
        return streamSchema -> new GcsCsvBigQueryRecordFormatter(streamSchema, namingResolver);
    }



    private ParsedCatalog parseCatalog( final ConfiguredAirbyteCatalog catalog) {
        return catalogParser.parseCatalog(catalog);
    }

    private SerializedAirbyteMessageConsumer getStandardRecordConsumer(final BigQuery bigquery,
                                                                       final BigQueryConnectorConfiguration configuration,
                                                                       final ConfiguredAirbyteCatalog catalog,
                                                                       final ParsedCatalog parsedCatalog,
                                                                       final Consumer<AirbyteMessage> outputRecordCollector)
            throws Exception {
        typerDeduper.prepareTables();
        final Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>>> writeConfigs = getUploaderMap(
                bigquery,
                configuration,
                catalog,
                parsedCatalog);

        final String bqNamespace = bigQueryUtils.getDatasetId(configuration);

        return new BigQueryRecordStandardConsumer(
                outputRecordCollector,
                () -> {
                    // Set up our raw tables
                    writeConfigs.get().forEach((streamId, uploader) -> {
                        final StreamConfig stream = parsedCatalog.getStream(streamId);
                        if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
                            // For streams in overwrite mode, truncate the raw table.
                            // non-1s1t syncs actually overwrite the raw table at the end of the sync, so we only do this in
                            // 1s1t mode.
                            final TableId rawTableId = TableId.of(stream.id().rawNamespace(), stream.id().rawName());
                            LOGGER.info("Deleting Raw table {}", rawTableId);
                            if (!bigquery.delete(rawTableId)) {
                                LOGGER.info("Raw table {} not found, continuing with creation", rawTableId);
                            }
                            LOGGER.info("Creating table {}", rawTableId);
                            bigQueryUtils.createPartitionedTableIfNotExists(bigquery, rawTableId, DefaultBigQueryRecordFormatter.SCHEMA_V2);
                        } else {
                            uploader.createRawTable();
                        }
                    });
                },
                (hasFailed, streamSyncSummaries) -> {
                    try {
                        Thread.sleep(30 * 1000);
                        typerDeduper.typeAndDedupe(streamSyncSummaries);
                        typerDeduper.commitFinalTables();
                        typerDeduper.cleanup();
                    } catch (final Exception e) {
                        throw new RuntimeException(e);
                    }
                },
                bigquery,
                catalog,
                bqNamespace,
                writeConfigs);
    }

    protected Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>>> getUploaderMap(
            final BigQuery bigquery,
            final BigQueryConnectorConfiguration config,
            final ConfiguredAirbyteCatalog catalog,
            final ParsedCatalog parsedCatalog) {
        return () -> {
            final ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new ConcurrentHashMap<>();
            for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
                final AirbyteStream stream = configStream.getStream();
                final StreamConfig parsedStream;

                final String targetTableName;

                parsedStream = parsedCatalog.getStream(stream.getNamespace(), stream.getName());
                targetTableName = parsedStream.id().rawName();

                final UploaderConfig uploaderConfig = UploaderConfig
                        .builder()
                        .bigQuery(bigquery)
                        .configStream(configStream)
                        .parsedStream(parsedStream)
                        .config(config)
                        .formatterMap(getFormatterMap(stream.getJsonSchema()))
                        .targetTableName(targetTableName)
                        // This refers to whether this is BQ denormalized or not
                        .isDefaultAirbyteTmpSchema(isDefaultAirbyteTmpTableSchema())
                        .build();

                try {
                    putStreamIntoUploaderMap(stream, uploaderConfig, uploaderMap);
                } catch (final IOException e) {
                    throw new RuntimeException(e);
                }
            }
            return uploaderMap;
        };
    }

    protected void putStreamIntoUploaderMap(final AirbyteStream stream,
                                            final UploaderConfig uploaderConfig,
                                            final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap)
            throws IOException {
        uploaderMap.put(
                AirbyteStreamNameNamespacePair.fromAirbyteStream(stream),
                BigQueryUploaderFactory.getUploader(uploaderConfig, bigQueryUtils));
    }

    private TyperDeduper buildTyperDeduper(final BigQuerySqlGenerator sqlGenerator,
                                           final ParsedCatalog parsedCatalog,
                                           final BigQuery bigquery,
                                           final BigQueryConnectorConfiguration configuration) {
        final BigQueryV1V2Migrator migrator = new BigQueryV1V2Migrator(bigquery, namingResolver);
        final BigQueryV2TableMigrator v2RawTableMigrator = new BigQueryV2TableMigrator(bigquery);
        final BigQueryDestinationHandler destinationHandler = new BigQueryDestinationHandler(bigquery, configuration);

        if (configuration.isDisableTypeDedupe()) {
            return new NoOpTyperDeduperWithV1V2Migrations<>(
                    sqlGenerator, destinationHandler, parsedCatalog, migrator, v2RawTableMigrator, 8);
        }

        return new DefaultTyperDeduper<>(
                sqlGenerator,
                destinationHandler,
                parsedCatalog,
                migrator,
                v2RawTableMigrator,
                8);

    }

    /**
     * BigQuery might have different structure of the Temporary table. If this method returns TRUE,
     * temporary table will have only three common Airbyte attributes. In case of FALSE, temporary table
     * structure will be in line with Airbyte message JsonSchema.
     *
     * @return use default AirbyteSchema or build using JsonSchema
     */
    protected boolean isDefaultAirbyteTmpTableSchema() {
        return true;
    }

    protected Map<UploaderType, BigQueryRecordFormatter> getFormatterMap(final JsonNode jsonSchema) {
        return Map.of(
                UploaderType.STANDARD, new DefaultBigQueryRecordFormatter(jsonSchema, namingResolver),
                UploaderType.CSV, new GcsCsvBigQueryRecordFormatter(jsonSchema, namingResolver));
    }
}
