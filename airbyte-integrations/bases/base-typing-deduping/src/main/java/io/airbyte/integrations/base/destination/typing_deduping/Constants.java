package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Set;

//TODO these are in JavaBaseConstants but are not referencable from here
public class Constants {
    public static final String AIRBYTE_NAMESPACE_SCHEMA = "airbyte";

    public static final String COLUMN_NAME_DATA = "_airbyte_data";

    // v1
    public static final String COLUMN_NAME_AB_ID = "_airbyte_ab_id";
    public static final String COLUMN_NAME_EMITTED_AT = "_airbyte_emitted_at";

    // destination v2
    public static final String COLUMN_NAME_AB_RAW_ID = "_airbyte_raw_id";
    public static final String COLUMN_NAME_AB_LOADED_AT = "_airbyte_loaded_at";
    public static final String COLUMN_NAME_AB_EXTRACTED_AT = "_airbyte_extracted_at";

    public static final Set<String> RAW_TABLE_EXPECTED_V1_COLUMNS =
            Set.of(
                    COLUMN_NAME_AB_ID,
                    COLUMN_NAME_EMITTED_AT,
                    COLUMN_NAME_DATA
            );

    public static final Set<String> RAW_TABLE_EXPECTED_V2_COLUMNS =
            Set.of(
                    COLUMN_NAME_AB_RAW_ID,
                    COLUMN_NAME_AB_LOADED_AT,
                    COLUMN_NAME_AB_EXTRACTED_AT,
                    COLUMN_NAME_DATA
            );

}
