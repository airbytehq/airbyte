/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.cdk

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.snowflake.spec.CredentialsSpecification
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.util.function.Supplier

internal const val AUTH_TYPE_PROPERTY = "\"auth_type\""

internal const val CREDENTIALS_PROPERTY = "\"credentials\""
internal const val PASSWORD_PROPERTY = "\"password\""

internal val CREDENTIALS_REGEX = """$CREDENTIALS_PROPERTY\s*:\s*\{\s*([^}]*)""".toRegex()
internal val PASSWORD_REGEX = """$PASSWORD_PROPERTY\s*:\s*"([^"}]*)""".toRegex()

private val logger = KotlinLogging.logger {}

@VisibleForTesting
fun migrateJson(json: String): String =
    if (!json.contains(CREDENTIALS_PROPERTY) && json.contains(PASSWORD_PROPERTY)) {
        migrateRootLevelPassword(json)
    } else if (json.contains(CREDENTIALS_PROPERTY) && !json.contains(AUTH_TYPE_PROPERTY)) {
        migrationMissingAuthType(json)
    } else {
        json
    }

internal fun migrationMissingAuthType(json: String): String {
    logger.info {
        "Detected legacy specification with credentials without auth type.  Attempting to migration configuration..."
    }
    val result = CREDENTIALS_REGEX.find(json)
    return result?.let {
        val credentials = result.groupValues[1]
        val authType =
            if (credentials.contains(PASSWORD_PROPERTY))
                CredentialsSpecification.Type.USERNAME_PASSWORD.authTypeName
            else CredentialsSpecification.Type.PRIVATE_KEY.authTypeName
        json.replace(
            CREDENTIALS_REGEX,
            Regex.escapeReplacement(
                "$CREDENTIALS_PROPERTY:{$AUTH_TYPE_PROPERTY:\"$authType\",$credentials}"
            )
        )
    }
        ?: json
}

internal fun migrateRootLevelPassword(json: String): String {
    logger.info {
        "Detected legacy specification with root level password.  Attempting to migration configuration..."
    }
    val result = PASSWORD_REGEX.find(json)
    return result?.let {
        val password = result.groupValues[1]
        json
            .replace(
                PASSWORD_REGEX,
                "$CREDENTIALS_PROPERTY:{$AUTH_TYPE_PROPERTY:\"${CredentialsSpecification.Type.USERNAME_PASSWORD.authTypeName}\",$PASSWORD_PROPERTY:\"$password\"}"
            )
            .replace("}\"", "}")
    }
        ?: json
}
/**
 * This is a custom override of the [ConfigurationSpecificationSupplier] in the CDK in order to
 * handle multiple types of legacy configurations for the Snowflake destination and coerce them into
 * the current configuration that is strongly typed/validated. This implementation handles two
 * specific legacy cases:
 *
 * <ol>
 * ```
 *     <li>Configuration with the <code>password</code> field at the top level of the configuration JSON document/li>
 *     <li>Configuration with a credentials block without an <code>auth_type</code> property</li>
 * ```
 * </ol>
 *
 * In both cases, this implementation attempts to find and extract the data listed above and convert
 * it to conform with the current [SnowflakeSpecification] format.
 */
@Singleton
@Replaces(ConfigurationSpecificationSupplier::class)
class SnowflakeMigratingConfigurationSpecificationSupplier(
    @param:Value("\${${CONNECTOR_CONFIG_PREFIX}.json}")
    private val jsonPropertyValue: String? = null,
) : Supplier<SnowflakeSpecification> {
    val specificationJavaClass: Class<SnowflakeSpecification> = SnowflakeSpecification::class.java

    @Suppress("UNCHECKED_CAST")
    val jsonSchema: JsonNode by lazy {
        ValidatedJsonUtils.generateAirbyteJsonSchema(specificationJavaClass)
    }

    override fun get(): SnowflakeSpecification {
        val jsonMicronautFallback: String by lazy {
            try {
                Jsons.writeValueAsString(SnowflakeSpecification())
            } catch (_: Exception) {
                throw ConfigErrorException(
                    "failed to serialize fallback instance for $specificationJavaClass"
                )
            }
        }
        val json: String = migrateJson(jsonPropertyValue ?: jsonMicronautFallback)
        return ValidatedJsonUtils.parseUnvalidated(json, specificationJavaClass)
    }
}
