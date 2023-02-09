/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

public final class JavaBaseConstants {

  private JavaBaseConstants() {}

  public static final String ARGS_CONFIG_KEY = "config";
  public static final String ARGS_CATALOG_KEY = "catalog";
  public static final String ARGS_STATE_KEY = "state";

  public static final String ARGS_CONFIG_DESC = "path to the json configuration file";
  public static final String ARGS_CATALOG_DESC = "input path for the catalog";
  public static final String ARGS_PATH_DESC = "path to the json-encoded state file";

  public static final String COLUMN_NAME_AB_ID = "_airbyte_ab_id";
  public static final String COLUMN_NAME_EMITTED_AT = "_airbyte_emitted_at";
  public static final String COLUMN_NAME_DATA = "_airbyte_data";

}
