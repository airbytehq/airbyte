/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.config

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.ConfigurationProperties
import io.micronaut.core.util.StringUtils

/**
 * Micronaut configured properties holder for the Airbyte configured catalog provided
 * to the connector CLI as an argument.
 */
@ConfigurationProperties("airbyte.connector.catalog")
@SuppressFBWarnings(
    value = ["NP_NONNULL_RETURN_VIOLATION"],
    justification = "Uses dependency injection",
)
class AirbyteConfiguredCatalog {
    lateinit var configured: String

    fun getConfiguredCatalog(): ConfiguredAirbyteCatalog {
        return if (StringUtils.isNotEmpty(configured)) {
            Jsons.deserialize(
                configured,
                ConfiguredAirbyteCatalog::class.java,
            )
        } else {
            ConfiguredAirbyteCatalog()
        }
    }
}
