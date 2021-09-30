/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

public class JavaBaseConstants {

  public static String ARGS_CONFIG_KEY = "config";
  public static String ARGS_CATALOG_KEY = "catalog";
  public static String ARGS_STATE_KEY = "state";

  public static String ARGS_CONFIG_DESC = "path to the json configuration file";
  public static String ARGS_CATALOG_DESC = "input path for the catalog";
  public static String ARGS_PATH_DESC = "path to the json-encoded state file";

  public static String COLUMN_NAME_AB_ID = "_airbyte_ab_id";
  public static String COLUMN_NAME_EMITTED_AT = "_airbyte_emitted_at";
  public static String COLUMN_NAME_DATA = "_airbyte_data";

}
