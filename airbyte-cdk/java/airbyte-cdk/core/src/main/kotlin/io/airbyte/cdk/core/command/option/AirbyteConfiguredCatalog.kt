/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.command.option

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.ConfigurationProperties

/**
 * Micronaut configured properties holder for the Airbyte configured catalog provided to the
 * connector CLI as an argument.
 */
@ConfigurationProperties("airbyte.connector.catalog")
@SuppressFBWarnings(
    value = ["NP_NONNULL_RETURN_VIOLATION"],
    justification = "Uses dependency injection",
)
class AirbyteConfiguredCatalog {
    lateinit var json: String

    fun getConfiguredCatalog(): ConfiguredAirbyteCatalog {
        return if (json.isNotBlank()) {
            Jsons.deserialize(
                json,
                ConfiguredAirbyteCatalog::class.java,
            )
        } else {
            ConfiguredAirbyteCatalog()
        }
    }
}
