package io.airbyte.cdk.core.config.annotation

import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.lang.annotation.Documented

@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.RUNTIME)
@Documented
annotation class ConnectorSpecificationDefinition(
    val changelogUrl: String,
    val documentationUrl: String,
    val protocolVersion: String,
    val supportsIncremental: Boolean,
    val supportsNormalization: Boolean,
    val supportsDBT: Boolean,
    val supportedDestinationSyncModes: Array<DestinationSyncMode>,


    )
