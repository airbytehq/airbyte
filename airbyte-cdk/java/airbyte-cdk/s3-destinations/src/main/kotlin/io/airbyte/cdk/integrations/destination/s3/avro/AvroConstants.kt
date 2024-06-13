/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import tech.allegro.schema.json2avro.converter.JsonAvroConverter

class AvroConstants {

    companion object {
        // Field name with special character
        const val DOC_KEY_VALUE_DELIMITER: String = ":"
        const val DOC_KEY_ORIGINAL_NAME: String = "_airbyte_original_name"
        const val AVRO_EXTRA_PROPS_FIELD: String = "_airbyte_additional_properties"

        // This set must include _ab_additional_col in source_s3/source_files_abstract/stream.py
        val JSON_EXTRA_PROPS_FIELDS: Set<String> =
            setOf("_ab_additional_properties", AVRO_EXTRA_PROPS_FIELD)

        @JvmField val NAME_TRANSFORMER: AvroNameTransformer = AvroNameTransformer()

        @JvmField
        val JSON_CONVERTER: JsonAvroConverter =
            JsonAvroConverter.builder()
                .setNameTransformer { name: String ->
                    NAME_TRANSFORMER.getIdentifier(
                        name,
                    )
                }
                .setJsonAdditionalPropsFieldNames(JSON_EXTRA_PROPS_FIELDS)
                .setAvroAdditionalPropsFieldName(AVRO_EXTRA_PROPS_FIELD)
                .build()
    }
}
