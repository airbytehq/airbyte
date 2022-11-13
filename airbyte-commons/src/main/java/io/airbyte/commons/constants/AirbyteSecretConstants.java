/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.constants;

/**
 * Collection of constants related to Airbyte secrets defined in connector configurations.
 */
public final class AirbyteSecretConstants {

  /**
   * The name of a configuration property field that has been identified as a secret.
   */
  public static final String AIRBYTE_SECRET_FIELD = "airbyte_secret";

  /**
   * Mask value that is displayed in place of a value associated with an airbyte secret.
   */
  public static final String SECRETS_MASK = "**********";

  private AirbyteSecretConstants() {
    // Private constructor to prevent instantiation
  }

}
