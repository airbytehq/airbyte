/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import com.github.victools.jsonschema.generator.SchemaGenerator
import io.airbyte.cdk.core.config.annotation.ConnectorSpecificationDefinition
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.OperationExecutionException
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.net.URI

private val logger = KotlinLogging.logger {}

@Singleton
@Named("specOperationExecutor")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "spec",
)
class DefaultSpecOperationExecutor(
    @Value("\${airbyte.connector.configuration.class}") private val connectorConfigurationClass: String,
    private val specGenerator: SchemaGenerator,
    @Value("\${airbyte.connector.specification.file:spec.json}")private val specFile: String) : OperationExecutor {
    override fun execute(): Result<AirbyteMessage> {
        try {
            val configurationClass = this.javaClass.classLoader.loadClass(connectorConfigurationClass)
            val jsonSchema = specGenerator.generateSchema(configurationClass)
            val connectorSpecificationDefinition: ConnectorSpecificationDefinition? = getConnectionSpecificationAnnotation(configurationClass)
            val connectorSpecification = ConnectorSpecification()
            connectorSpecification.connectionSpecification = Jsons.deserialize(jsonSchema.toString())
            connectorSpecificationDefinition?.let {
                connectorSpecification.changelogUrl = URI(it.changelogUrl)
                connectorSpecification.documentationUrl = URI(it.documentationUrl)
                connectorSpecification.protocolVersion = it.protocolVersion
                connectorSpecification.supportedDestinationSyncModes = it.supportedDestinationSyncModes.toList()
                connectorSpecification.supportsDBT = it.supportsDBT
                connectorSpecification.supportsIncremental = it.supportsIncremental
                connectorSpecification.supportsNormalization = it.supportsNormalization
            }

            logger.info { "JsonSchema spec: \n${Jsons.jsonNode(connectorSpecification).toPrettyString()}"}
//            logger.info { "Spec file: \n${MoreResources.readResource(specFile)}"}

            return Result.success(AirbyteMessage().withType(AirbyteMessage.Type.SPEC).withSpec(connectorSpecification))
        } catch (e: Exception) {
            return Result.failure(OperationExecutionException("Failed to retrieve specification from connector.", e))
        }
//        try {
//            val resourceString = MoreResources.readResource(specFile)
//            val connectorSpecification =
//                Jsons.deserialize(
//                    resourceString,
//                    ConnectorSpecification::class.java,
//                )
//            return Result.success(AirbyteMessage().withType(AirbyteMessage.Type.SPEC).withSpec(connectorSpecification))
//        } catch (e: Exception) {
//            return Result.failure(OperationExecutionException("Failed to retrieve specification from connector.", e))
//        }
    }

    private fun getConnectionSpecificationAnnotation(configurationClass: Class<*>): ConnectorSpecificationDefinition? {
        return configurationClass.annotations.find { it is ConnectorSpecificationDefinition } as? ConnectorSpecificationDefinition
    }
}
