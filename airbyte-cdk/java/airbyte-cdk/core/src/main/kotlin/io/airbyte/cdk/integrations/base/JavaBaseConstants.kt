/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import java.util.Locale
import org.apache.commons.lang3.StringUtils

fun upperQuoted(column: String): String {
    return StringUtils.wrap(column.uppercase(Locale.getDefault()), "\"")
}

object JavaBaseConstants {
    const val ARGS_CONFIG_KEY: String = "config"
    const val ARGS_CATALOG_KEY: String = "catalog"
    const val ARGS_STATE_KEY: String = "state"

    const val ARGS_CONFIG_DESC: String = "path to the json configuration file"
    const val ARGS_CATALOG_DESC: String = "input path for the catalog"
    const val ARGS_PATH_DESC: String = "path to the json-encoded state file"

    const val COLUMN_NAME_AB_ID: String = "_airbyte_ab_id"
    const val COLUMN_NAME_EMITTED_AT: String = "_airbyte_emitted_at"
    const val COLUMN_NAME_DATA: String = "_airbyte_data"
    @JvmField
    val LEGACY_RAW_TABLE_COLUMNS: List<String> =
        listOf(COLUMN_NAME_AB_ID, COLUMN_NAME_DATA, COLUMN_NAME_EMITTED_AT)

    // destination v2
    const val COLUMN_NAME_AB_RAW_ID: String = "_airbyte_raw_id"
    const val COLUMN_NAME_AB_LOADED_AT: String = "_airbyte_loaded_at"
    const val COLUMN_NAME_AB_EXTRACTED_AT: String = "_airbyte_extracted_at"
    const val COLUMN_NAME_AB_META: String = "_airbyte_meta"
    const val COLUMN_NAME_AB_GENERATION_ID: String = "_airbyte_generation_id"

    const val AIRBYTE_META_SYNC_ID_KEY = "sync_id"

    // Meta was introduced later, so to avoid triggering raw table soft-reset in v1->v2
    // use this column list.
    @JvmField
    val V2_RAW_TABLE_COLUMN_NAMES_WITHOUT_META: List<String> =
        listOf(
            COLUMN_NAME_AB_RAW_ID,
            COLUMN_NAME_AB_EXTRACTED_AT,
            COLUMN_NAME_AB_LOADED_AT,
            COLUMN_NAME_DATA,
        )
    @JvmField
    val V2_RAW_TABLE_COLUMN_NAMES: List<String> =
        listOf(
            COLUMN_NAME_AB_RAW_ID,
            COLUMN_NAME_AB_EXTRACTED_AT,
            COLUMN_NAME_AB_LOADED_AT,
            COLUMN_NAME_DATA,
            COLUMN_NAME_AB_META,
        )
    @JvmField
    val V2_RAW_TABLE_COLUMN_NAMES_WITH_GENERATION: List<String> =
        listOf(
            COLUMN_NAME_AB_RAW_ID,
            COLUMN_NAME_AB_EXTRACTED_AT,
            COLUMN_NAME_AB_LOADED_AT,
            COLUMN_NAME_DATA,
            COLUMN_NAME_AB_META,
            COLUMN_NAME_AB_GENERATION_ID,
        )
    @JvmField
    val V2_FINAL_TABLE_METADATA_COLUMNS: List<String> =
        listOf(
            COLUMN_NAME_AB_RAW_ID,
            COLUMN_NAME_AB_EXTRACTED_AT,
            COLUMN_NAME_AB_META,
            COLUMN_NAME_AB_GENERATION_ID
        )

    const val DEFAULT_AIRBYTE_INTERNAL_NAMESPACE: String = "airbyte_internal"
    enum class DestinationColumns(val rawColumns: List<String>) {
        V2_WITH_META(V2_RAW_TABLE_COLUMN_NAMES),
        V2_WITHOUT_META(V2_RAW_TABLE_COLUMN_NAMES_WITHOUT_META),
        V2_WITH_GENERATION(V2_RAW_TABLE_COLUMN_NAMES_WITH_GENERATION),
        LEGACY(LEGACY_RAW_TABLE_COLUMNS)
    }
}
