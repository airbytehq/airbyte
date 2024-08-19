/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination

/**
 * Destination have their own Naming conventions (which characters are valid or rejected in
 * identifiers names) This class transform a random string used to a valid identifier names for each
 * specific destination.
 */
interface NamingConventionTransformer {
    /**
     * Handle Naming Conversions of an input name to output a valid identifier name for the desired
     * destination.
     *
     * @param name of the identifier to check proper naming conventions
     * @return modified name with invalid characters replaced by '_' and adapted for the chosen
     * destination.
     */
    fun getIdentifier(name: String): String

    /**
     * Handle naming conversions of an input name to output a valid namespace for the desired
     * destination.
     */
    fun getNamespace(namespace: String): String

    /**
     * Same as getIdentifier but returns also the name of the table for storing raw data
     *
     * @param name of the identifier to check proper naming conventions
     * @return modified name with invalid characters replaced by '_' and adapted for the chosen
     * destination.
     */
    @Deprecated("as this is very SQL specific, prefer using getIdentifier instead")
    fun getRawTableName(name: String): String

    /**
     * Same as getIdentifier but returns also the name of the table for storing tmp data
     *
     * @param name of the identifier to check proper naming conventions
     * @return modified name with invalid characters replaced by '_' and adapted for the chosen
     * destination.
     */
    @Deprecated("as this is very SQL specific, prefer using getIdentifier instead")
    fun getTmpTableName(name: String): String

    @Suppress("DEPRECATION")
    fun getTmpTableName(streamName: String, randomSuffix: String): String {
        return getTmpTableName(streamName)
    }

    fun convertStreamName(input: String): String

    fun applyDefaultCase(input: String): String
}
