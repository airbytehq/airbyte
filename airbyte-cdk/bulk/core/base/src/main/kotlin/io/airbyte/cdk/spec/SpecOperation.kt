/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.spec

import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.DefaultImplementation
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.net.URI

@Singleton
@Requires(property = Operation.PROPERTY, value = "spec")
class SpecOperation(
    @Value("\${airbyte.connector.metadata.documentation-url}") val documentationUrl: String,
    val specificationFactory: SpecificationFactory,
    val outputConsumer: OutputConsumer,
) : Operation {
    override fun execute() {
        val spec = specificationFactory.create().withDocumentationUrl(URI.create(documentationUrl))
        outputConsumer.accept(spec)
    }
}

interface SpecificationFactory {
    fun create(): ConnectorSpecification
}

@Singleton
class ConfigurationSupplierSpecificationFactory(
    val configJsonObjectSupplier: ConfigurationSpecificationSupplier<*>,
    val extendSpecification: SpecificationExtender,
) : SpecificationFactory {
    override fun create(): ConnectorSpecification {
        return extendSpecification(
            ConnectorSpecification()
                .withConnectionSpecification(configJsonObjectSupplier.jsonSchema)
        )
    }
}

interface SpecificationExtender : (ConnectorSpecification) -> ConnectorSpecification

@Singleton
@DefaultImplementation
class IdentitySpecificationExtender : SpecificationExtender {
    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        return specification
    }
}
