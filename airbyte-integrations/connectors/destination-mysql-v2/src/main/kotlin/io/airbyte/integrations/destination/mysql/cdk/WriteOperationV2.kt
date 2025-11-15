package io.airbyte.integrations.destination.mysql.cdk

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.dataflow.DestinationLifecycle
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Primary
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperationV2(
    private val d: DestinationLifecycle,
) : Operation {
    override fun execute() {
        d.run()
    }
}
