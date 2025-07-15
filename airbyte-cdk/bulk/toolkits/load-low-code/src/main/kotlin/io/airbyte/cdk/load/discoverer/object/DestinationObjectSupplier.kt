package io.airbyte.cdk.load.discoverer.`object`

interface DestinationObjectSupplier {
    fun get(): List<DestinationObject>
}
