package io.airbyte.integrations.destination.s3.util

import io.airbyte.cdk.core.config.AirbyteConfiguredCatalog
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.WriteConfig
import io.airbyte.integrations.destination.s3.config.properties.S3ConnectorConfiguration
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.micronaut.context.annotation.Requires
import io.micronaut.core.util.StringUtils
import jakarta.inject.Singleton
import org.joda.time.DateTime
import org.joda.time.DateTimeZone
import java.lang.String.join

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
class WriteConfigGenerator(
    private val airbyteConfiguredCatalog: AirbyteConfiguredCatalog,
    private val s3ConnectorConfiguration: S3ConnectorConfiguration,
    private val s3StorageOperations: S3StorageOperations,
) {

    fun toWriteConfigs(): List<WriteConfig> {
        return airbyteConfiguredCatalog.getConfiguredCatalog().streams
            .stream()
            .map(this::toWriteConfig)
            .toList()
    }

    private fun toWriteConfig(stream: ConfiguredAirbyteStream): WriteConfig {
        require(stream.destinationSyncMode != null) { "Undefined destination sync mode" }
        val abStream = stream.stream
        val namespace: String? = abStream.namespace
        val streamName = abStream.name
        val bucketPath: String? = s3ConnectorConfiguration.s3BucketPath
        val customOutputFormat = join("/", bucketPath, getPathFormat())
        val fullOutputPath: String = s3StorageOperations.getBucketObjectPath(
            namespace,
            streamName,
            DateTime.now(DateTimeZone.UTC),
            customOutputFormat
        )
        val syncMode = stream.destinationSyncMode
        val writeConfig = WriteConfig(namespace, streamName, bucketPath, customOutputFormat, fullOutputPath, syncMode)
        return writeConfig
    }

    private fun getPathFormat(): String {
        return if(StringUtils.isNotEmpty(s3ConnectorConfiguration.s3PathFormat)) {
            s3ConnectorConfiguration.s3PathFormat!!
        } else {
            S3DestinationConstants.DEFAULT_PATH_FORMAT
        }
    }
}