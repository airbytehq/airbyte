/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination;

/**
 * Destination have their own Naming conventions (which characters are valid or rejected in
 * identifiers names) This class transform a random string used to a valid identifier names for each
 * specific destination.
 */
public interface NamingConventionTransformer {

  /**
   * Handle Naming Conversions of an input name to output a valid identifier name for the desired
   * destination.
   *
   * @param name of the identifier to check proper naming conventions
   * @return modified name with invalid characters replaced by '_' and adapted for the chosen
   *         destination.
   */
  String getIdentifier(String name);

  /**
   * Handle naming conversions of an input name to output a valid namespace for the desired
   * destination.
   */
  String getNamespace(String namespace);

  /**
   * Same as getIdentifier but returns also the name of the table for storing raw data
   *
   * @param name of the identifier to check proper naming conventions
   * @return modified name with invalid characters replaced by '_' and adapted for the chosen
   *         destination.
   *
   * @deprecated as this is very SQL specific, prefer using getIdentifier instead
   */
  @Deprecated
  String getRawTableName(String name);

  /**
   * Same as getIdentifier but returns also the name of the table for storing tmp data
   *
   * @param name of the identifier to check proper naming conventions
   * @return modified name with invalid characters replaced by '_' and adapted for the chosen
   *         destination.
   *
   * @deprecated as this is very SQL specific, prefer using getIdentifier instead
   */
  @Deprecated
  String getTmpTableName(String name);

  String convertStreamName(final String input);

  String applyDefaultCase(final String input);

}
