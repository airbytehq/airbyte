package io.airbyte.integrations.destination.shelby

import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageSpec
import io.airbyte.cdk.load.command.dlq.ObjectStorageSpec
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Shelby Goes Fast")
@JsonSchemaInject
class ShelbySpecification : ConfigurationSpecification()
{
    val objectStorageConfig: ObjectStorageSpec = DisabledObjectStorageSpec()

}

@Singleton
class ShelbySpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.APPEND,
        )

    override val supportsIncremental = true
}
