/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

/**
 * Collection of toys database related constants.
 */
public final class ToysDatabaseConstants {

  /**
   * Logical name of the Toys database.
   */
  public static final String DATABASE_LOGGING_NAME = "toys";

  /**
   * Expected table to be present in the Toys database after creation.
   */
  public static final String TABLE_NAME = "toy_cars";

  /**
   * Path to the script that contains the initial schema definition for the Toys database.
   */
  public static final String SCHEMA_PATH = "toys_database/schema.sql";

  /**
   * Private constructor to prevent instantiation.
   */
  private ToysDatabaseConstants() {}

}
