/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.databind.PropertyNamingStrategies
import io.airbyte.cdk.util.ResourceUtils
import io.micronaut.context.env.MapPropertySource
import io.micronaut.context.env.yaml.YamlPropertySourceLoader
import java.net.URL

/** Loads the contents of the connector's metadata.yaml file as Micronaut properties. */
class MetadataYamlPropertySource : MapPropertySource(METADATA_YAML, loadFromResource()) {
    companion object {
        const val METADATA_YAML = "metadata.yaml"
        const val PROPERTY_PREFIX = "airbyte.connector.metadata"

        fun loadFromResource(): Map<String, Any?> {
            val resourceURL: URL = ResourceUtils.getResource(METADATA_YAML)
            val rawProperties: Map<String, Any?> =
                YamlPropertySourceLoader()
                    .read(
                        METADATA_YAML,
                        resourceURL.openStream(),
                    )

            return rawProperties.mapKeys { (key: String, _) ->
                val stripped: String = key.removePrefix("data.")
                val kebabCase: String =
                    PropertyNamingStrategies.KebabCaseStrategy.INSTANCE.translate(stripped)
                "${PROPERTY_PREFIX}.$kebabCase"
            }
        }
    }
}
