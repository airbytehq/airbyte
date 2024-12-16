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
    val configJsonObjectSupplier: ConfigurationSpecificationSupplier<*>,
    val extendSpecification: SpecificationExtender,
    val outputConsumer: OutputConsumer,
) : Operation {
    override fun execute() {
        val spec =
            ConnectorSpecification()
                .withDocumentationUrl(URI.create(documentationUrl))
                .withConnectionSpecification(configJsonObjectSupplier.jsonSchema)
        outputConsumer.accept(extendSpecification(spec))
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
