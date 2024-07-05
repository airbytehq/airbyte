/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import com.fasterxml.jackson.databind.JsonNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.factory.DataSourceFactory.create
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility.emitConfigErrorTrace
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.getRawNamespaceOverride
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcV1V2Migrator
import io.airbyte.cdk.integrations.destination.s3.AesCbcEnvelopeEncryption
import io.airbyte.cdk.integrations.destination.s3.EncryptionConfig
import io.airbyte.cdk.integrations.destination.s3.EncryptionConfig.Companion.fromJson
import io.airbyte.cdk.integrations.destination.s3.NoEncryption
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks.attemptS3WriteAndDelete
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.staging.StagingConsumerFactory.Companion.builder
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations
import io.airbyte.integrations.base.destination.typing_deduping.NoopV2TableMigrator
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants
import io.airbyte.integrations.destination.redshift.operations.RedshiftS3StagingSqlOperations
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDestinationHandler
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftRawTableAirbyteMetaMigration
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftState
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSuperLimitationTransformer
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.time.Duration
import java.util.function.Consumer
import javax.sql.DataSource
import org.apache.commons.lang3.NotImplementedException
import org.apache.commons.lang3.StringUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class RedshiftStagingS3Destination :
    AbstractJdbcDestination<RedshiftState>(
        RedshiftInsertDestination.DRIVER_CLASS,
        RedshiftSQLNameTransformer(),
        RedshiftSqlOperations()
    ),
    Destination {
    private fun isEphemeralKeysAndPurgingStagingData(
        config: JsonNode,
        encryptionConfig: EncryptionConfig
    ): Boolean {
        return !isPurgeStagingData(config) &&
            encryptionConfig is AesCbcEnvelopeEncryption &&
            encryptionConfig.keyType == AesCbcEnvelopeEncryption.KeyType.EPHEMERAL
    }

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        val s3Config: S3DestinationConfig =
            S3DestinationConfig.getS3DestinationConfig(RedshiftUtil.findS3Options(config))
        val encryptionConfig =
            if (config.has(RedshiftDestinationConstants.UPLOADING_METHOD))
                fromJson(
                    config[RedshiftDestinationConstants.UPLOADING_METHOD][JdbcUtils.ENCRYPTION_KEY]
                )
            else NoEncryption()
        if (isEphemeralKeysAndPurgingStagingData(config, encryptionConfig)) {
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    "You cannot use ephemeral keys and disable purging your staging data. This would produce S3 objects that you cannot decrypt."
                )
        }
        attemptS3WriteAndDelete(
            S3StorageOperations(RedshiftSQLNameTransformer(), s3Config.getS3Client(), s3Config),
            s3Config,
            s3Config.bucketPath
        )

        val nameTransformer = namingResolver
        val redshiftS3StagingSqlOperations =
            RedshiftS3StagingSqlOperations(
                nameTransformer,
                s3Config.getS3Client(),
                s3Config,
                encryptionConfig
            )
        val dataSource = getDataSource(config)
        try {
            val database: JdbcDatabase = DefaultJdbcDatabase(dataSource)
            val outputSchema =
                super.namingResolver.getIdentifier(config[JdbcUtils.SCHEMA_KEY].asText())
            attemptTableOperations(
                outputSchema,
                database,
                nameTransformer,
                redshiftS3StagingSqlOperations,
                false
            )
            RedshiftUtil.checkSvvTableAccess(database)
            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (e: ConnectionErrorException) {
            val message = getErrorMessage(e.stateCode, e.errorCode, e.exceptionMessage, e)
            emitConfigErrorTrace(e, message)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(message)
        } catch (e: Exception) {
            LOGGER.error("Exception while checking connection: ", e)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    """
    Could not connect with provided configuration. 
    ${e.message}
    """.trimIndent()
                )
        } finally {
            try {
                close(dataSource)
            } catch (e: Exception) {
                LOGGER.warn("Unable to close data source.", e)
            }
        }
    }

    override fun getDataSource(config: JsonNode): DataSource {
        val jdbcConfig: JsonNode = RedshiftInsertDestination.Companion.getJdbcConfig(config)
        return create(
            jdbcConfig[JdbcUtils.USERNAME_KEY].asText(),
            if (jdbcConfig.has(JdbcUtils.PASSWORD_KEY)) jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
            else null,
            RedshiftInsertDestination.Companion.DRIVER_CLASS,
            jdbcConfig[JdbcUtils.JDBC_URL_KEY].asText(),
            getDefaultConnectionProperties(config),
            Duration.ofMinutes(2)
        )
    }

    override val namingResolver: NamingConventionTransformer
        get() = RedshiftSQLNameTransformer()

    override fun getDefaultConnectionProperties(config: JsonNode): Map<String, String> {
        // TODO: Pull common code from RedshiftInsertDestination and RedshiftStagingS3Destination
        // into a
        // base class.
        // The following properties can be overriden through jdbcUrlParameters in the config.
        val connectionOptions: MutableMap<String, String> = HashMap()
        // Redshift properties
        // https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-configuration-options.html#jdbc20-connecttimeout-option
        // connectTimeout is different from Hikari pool's connectionTimout, driver defaults to
        // 10seconds so
        // increase it to match hikari's default
        connectionOptions["connectTimeout"] = "120"
        // HikariPool properties
        // https://github.com/brettwooldridge/HikariCP?tab=readme-ov-file#frequently-used
        // connectionTimeout is set explicitly to 2 minutes when creating data source.
        // Do aggressive keepAlive with minimum allowed value, this only applies to connection
        // sitting idle
        // in the pool.
        connectionOptions["keepaliveTime"] = Duration.ofSeconds(30).toMillis().toString()
        connectionOptions.putAll(RedshiftInsertDestination.Companion.SSL_JDBC_PARAMETERS)
        return connectionOptions
    }

    // this is a no op since we override getDatabase.
    override fun toJdbcConfig(config: JsonNode): JsonNode {
        return emptyObject()
    }

    override fun getSqlGenerator(config: JsonNode): JdbcSqlGenerator {
        return RedshiftSqlGenerator(namingResolver, config)
    }

    override fun getDestinationHandler(
        databaseName: String,
        database: JdbcDatabase,
        rawTableSchema: String
    ): JdbcDestinationHandler<RedshiftState> {
        return RedshiftDestinationHandler(databaseName, database, rawTableSchema)
    }

    protected override fun getMigrations(
        database: JdbcDatabase,
        databaseName: String,
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<RedshiftState>
    ): List<Migration<RedshiftState>> {
        return java.util.List.of<Migration<RedshiftState>>(
            RedshiftRawTableAirbyteMetaMigration(database, databaseName)
        )
    }

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun getDataTransformer(
        parsedCatalog: ParsedCatalog?,
        defaultNamespace: String?
    ): StreamAwareDataTransformer {
        // Redundant override to keep in consistent with InsertDestination. TODO: Unify these 2
        // classes with
        // composition.
        return RedshiftSuperLimitationTransformer(parsedCatalog, defaultNamespace!!)
    }

    @Deprecated("")
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        throw NotImplementedException("Should use the getSerializedMessageConsumer instead")
    }

    @Throws(Exception::class)
    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer? {
        val encryptionConfig =
            if (config.has(RedshiftDestinationConstants.UPLOADING_METHOD))
                fromJson(
                    config[RedshiftDestinationConstants.UPLOADING_METHOD][JdbcUtils.ENCRYPTION_KEY]
                )
            else NoEncryption()
        val s3Options = RedshiftUtil.findS3Options(config)
        val s3Config: S3DestinationConfig = S3DestinationConfig.getS3DestinationConfig(s3Options)

        val defaultNamespace = config["schema"].asText()
        for (stream in catalog.streams) {
            if (StringUtils.isEmpty(stream.stream.namespace)) {
                stream.stream.namespace = defaultNamespace
            }
        }

        val sqlGenerator = RedshiftSqlGenerator(namingResolver, config)
        val parsedCatalog: ParsedCatalog
        val typerDeduper: TyperDeduper
        val database = getDatabase(getDataSource(config))
        val databaseName = config[JdbcUtils.DATABASE_KEY].asText()
        val catalogParser: CatalogParser
        val rawNamespace: String
        if (getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent) {
            rawNamespace = getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get()
            catalogParser = CatalogParser(sqlGenerator, rawNamespace)
        } else {
            rawNamespace = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
            catalogParser = CatalogParser(sqlGenerator, rawNamespace)
        }
        val redshiftDestinationHandler =
            RedshiftDestinationHandler(databaseName, database, rawNamespace)
        parsedCatalog = catalogParser.parseCatalog(catalog)
        val migrator = JdbcV1V2Migrator(namingResolver, database, databaseName)
        val v2TableMigrator = NoopV2TableMigrator()
        val disableTypeDedupe =
            config.has(DISABLE_TYPE_DEDUPE) && config[DISABLE_TYPE_DEDUPE].asBoolean(false)
        val redshiftMigrations: List<Migration<RedshiftState>> =
            getMigrations(database, databaseName, sqlGenerator, redshiftDestinationHandler)
        typerDeduper =
            if (disableTypeDedupe) {
                NoOpTyperDeduperWithV1V2Migrations(
                    sqlGenerator,
                    redshiftDestinationHandler,
                    parsedCatalog,
                    migrator,
                    v2TableMigrator,
                    redshiftMigrations
                )
            } else {
                DefaultTyperDeduper(
                    sqlGenerator,
                    redshiftDestinationHandler,
                    parsedCatalog,
                    migrator,
                    v2TableMigrator,
                    redshiftMigrations
                )
            }

        return builder(
                outputRecordCollector,
                database,
                RedshiftS3StagingSqlOperations(
                    namingResolver,
                    s3Config.getS3Client(),
                    s3Config,
                    encryptionConfig
                ),
                namingResolver,
                config,
                catalog,
                isPurgeStagingData(s3Options),
                typerDeduper,
                parsedCatalog,
                defaultNamespace,
                JavaBaseConstants.DestinationColumns.V2_WITH_META
            )
            .setDataTransformer(getDataTransformer(parsedCatalog, defaultNamespace))
            .build()
            .createAsync()
    }

    private fun isPurgeStagingData(config: JsonNode?): Boolean {
        return !config!!.has("purge_staging_data") || config["purge_staging_data"].asBoolean()
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(RedshiftStagingS3Destination::class.java)

        fun sshWrappedDestination(): Destination {
            return SshWrappedDestination(
                RedshiftStagingS3Destination(),
                JdbcUtils.HOST_LIST_KEY,
                JdbcUtils.PORT_LIST_KEY
            )
        }
    }
}
