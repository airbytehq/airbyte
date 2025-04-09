package io.airbyte.test

import io.airbyte.cdk.AirbyteDestinationRunner
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.command.gcs.GcsClientConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.gcs.GcsRegion
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecificationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.airbyte.cdk.load.write.object_storage.ObjectStorageStreamLoaderFactory
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.OutputStream

fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args)
}

@Singleton
class GcsSpec : ConfigurationSpecification() {}

@Factory
class GcsConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): GcsConfig<*> {
        return config as GcsConfig<*>
    }
}

@Singleton
class GcsConfigurationFactory :
    DestinationConfigurationFactory<GcsSpec, GcsConfig<*>> {
    override fun makeWithoutExceptionHandling(pojo: GcsSpec): GcsConfig<*> {
        return GcsConfig(ObjectStorageCompressionConfiguration(NoopProcessor))
    }
}

class GcsConfig<T : OutputStream>(override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>) : DestinationConfiguration(), GcsClientConfigurationProvider, ObjectStoragePathConfigurationProvider,
    ObjectStorageFormatConfigurationProvider, ObjectStorageCompressionConfigurationProvider<T>,
    ObjectStorageUploadConfigurationProvider {
    override val gcsClientConfiguration: GcsClientConfiguration
        get() = GcsClientConfiguration(
            gcsBucketName = "airbyte-integration-test-destination-gcs",
            path = "edgao_local_test",
            credential = GcsHmacKeyConfiguration("hunter", "hunter2"),
            region = GcsRegion.US_WEST1,
        )
    override val objectStoragePathConfiguration: ObjectStoragePathConfiguration
        get() = ObjectStoragePathConfiguration("", null, null)
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration
        get() = JsonFormatConfiguration()
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration
        get() = ObjectStorageUploadConfiguration()
}

@Singleton
class GcsV2Writer(
    private val streamLoaderFactory: ObjectStorageStreamLoaderFactory<GcsBlob, *>,
) : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return streamLoaderFactory.create(stream)
    }
}

@Singleton
class GcsObjectLoader(config: GcsConfig<*>) : ObjectLoader {
}

@Singleton
class GcsSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
        )
    override val supportsIncremental = true
}
