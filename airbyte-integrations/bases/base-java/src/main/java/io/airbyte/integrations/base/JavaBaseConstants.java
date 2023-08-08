/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import java.util.List;

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
  public static final List<String> LEGACY_COLUMN_NAMES = List.of(
      COLUMN_NAME_AB_ID,
      COLUMN_NAME_DATA,
      COLUMN_NAME_EMITTED_AT);

  // destination v2
  public static final String COLUMN_NAME_AB_RAW_ID = "_airbyte_raw_id";
  public static final String COLUMN_NAME_AB_LOADED_AT = "_airbyte_loaded_at";
  public static final String COLUMN_NAME_AB_EXTRACTED_AT = "_airbyte_extracted_at";
  public static final List<String> V2_COLUMN_NAMES = List.of(
      COLUMN_NAME_AB_RAW_ID,
      COLUMN_NAME_AB_EXTRACTED_AT,
      COLUMN_NAME_AB_LOADED_AT,
      COLUMN_NAME_DATA);

  public static final String AIRBYTE_NAMESPACE_SCHEMA = "airbyte";

}
