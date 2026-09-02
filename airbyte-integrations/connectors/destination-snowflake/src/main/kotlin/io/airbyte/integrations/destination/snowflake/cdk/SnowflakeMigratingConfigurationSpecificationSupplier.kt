/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
import io.airbyte.integrations.destination.snowflake.spec.USERNAME_PASSWORD_AUTH_TYPE
import io.airbyte.integrations.destination.snowflake.spec.USERNAME_PASSWORD_REMOVED_MESSAGE
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.util.function.Supplier

internal const val AUTH_TYPE_PROPERTY = "\"auth_type\""

internal const val CREDENTIALS_PROPERTY = "\"credentials\""
internal const val PASSWORD_PROPERTY = "\"password\""

internal val CREDENTIALS_REGEX = """$CREDENTIALS_PROPERTY\s*:\s*\{\s*([^}]*)""".toRegex()

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
        "Detected legacy specification with credentials without auth type. Rejecting configuration: username/password authentication is no longer supported."
    }
    val result = CREDENTIALS_REGEX.find(json)
    return result?.let {
        val credentials = result.groupValues[1]
        if (credentials.contains(PASSWORD_PROPERTY)) {
            throw ConfigErrorException(USERNAME_PASSWORD_REMOVED_MESSAGE)
        }
        json.replace(
            CREDENTIALS_REGEX,
            Regex.escapeReplacement(
                "$CREDENTIALS_PROPERTY:{$AUTH_TYPE_PROPERTY:\"${CredentialsSpecification.Type.PRIVATE_KEY.authTypeName}\",$credentials}"
            )
        )
    }
        ?: json
}

internal fun migrateRootLevelPassword(json: String): String {
    logger.info {
        "Detected legacy specification with root level password. Rejecting configuration: username/password authentication is no longer supported."
    }
    throw ConfigErrorException(USERNAME_PASSWORD_REMOVED_MESSAGE)
}
/**
 * This is a custom override of the [ConfigurationSpecificationSupplier] in the CDK in order to
 * reject legacy configurations that use password authentication and coerce key-pair configurations
 * into the current configuration that is strongly typed/validated. This implementation handles
 * these legacy cases:
 *
 * <ol>
 * ```
 *     <li>Configuration with the <code>password</code> field at the top level of the configuration JSON document</li>
 *     <li>Configuration with a credentials block without an <code>auth_type</code> property</li>
 * ```
 * </ol>
 *
 * Password-based configurations are rejected with an actionable configuration error. Key-pair
 * configurations without an auth type are converted to the current [SnowflakeSpecification] format.
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
        val migratedJson: String = migrateJson(jsonPropertyValue ?: jsonMicronautFallback)
        val authType =
            runCatching { Jsons.readTree(migratedJson) }
                .getOrNull()
                ?.path("credentials")
                ?.path("auth_type")
                ?.asText()
        if (authType == USERNAME_PASSWORD_AUTH_TYPE) {
            throw ConfigErrorException(USERNAME_PASSWORD_REMOVED_MESSAGE)
        }
        return ValidatedJsonUtils.parseUnvalidated(migratedJson, specificationJavaClass)
    }
}
