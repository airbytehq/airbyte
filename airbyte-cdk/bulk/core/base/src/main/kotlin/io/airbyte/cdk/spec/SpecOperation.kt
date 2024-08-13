/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.spec

import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.net.URI

@Singleton
@Requires(property = Operation.PROPERTY, value = "spec")
class SpecOperation(
    @Value("\${airbyte.connector.metadata.documentation-url}") val documentationUrl: String,
    val configJsonObjectSupplier: ConfigurationJsonObjectSupplier<*>,
    val outputConsumer: OutputConsumer,
) : Operation {
    override fun execute() {
        outputConsumer.accept(
            ConnectorSpecification()
                .withDocumentationUrl(URI.create(documentationUrl))
                .withConnectionSpecification(configJsonObjectSupplier.jsonSchema),
        )
    }
}
