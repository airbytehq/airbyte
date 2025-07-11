/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.test.fixtures.connector

import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog

class IntegrationTestOperations(
    private val configSpec: ConfigurationSpecification,
) {

    fun check(): Boolean {
        val output = CliRunner.source("check", configSpec).run()
        return output.records().isEmpty()
    }

    fun discover(): Map<String, AirbyteStream> {
        val output: BufferingOutputConsumer = CliRunner.source("discover", configSpec).run()
        val streams: Map<String, AirbyteStream> =
            output.catalogs().firstOrNull()?.streams?.filterNotNull()?.associateBy { it.name }
                ?: mapOf()
        return streams
    }

    fun sync(
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage> = listOf(),
        vararg featureFlags: FeatureFlag
    ): BufferingOutputConsumer {
        return CliRunner.source("read", configSpec, catalog, state, *featureFlags).run()
    }
}
