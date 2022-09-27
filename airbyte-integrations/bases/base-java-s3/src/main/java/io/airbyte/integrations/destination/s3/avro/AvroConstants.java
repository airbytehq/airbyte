/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import java.util.Set;
import tech.allegro.schema.json2avro.converter.JsonAvroConverter;

public class AvroConstants {

  // Field name with special character
  public static final String DOC_KEY_VALUE_DELIMITER = ":";
  public static final String DOC_KEY_ORIGINAL_NAME = "_airbyte_original_name";

  public static final String AVRO_EXTRA_PROPS_FIELD = "_airbyte_additional_properties";
  // This set must include _ab_additional_col in source_s3/source_files_abstract/stream.py
  public static final Set<String> JSON_EXTRA_PROPS_FIELDS = Set.of("_ab_additional_properties", AVRO_EXTRA_PROPS_FIELD);
  public static final AvroNameTransformer NAME_TRANSFORMER = new AvroNameTransformer();
  public static final JsonAvroConverter JSON_CONVERTER = JsonAvroConverter.builder()
      .setNameTransformer(NAME_TRANSFORMER::getIdentifier)
      .setJsonAdditionalPropsFieldNames(JSON_EXTRA_PROPS_FIELDS)
      .setAvroAdditionalPropsFieldName(AVRO_EXTRA_PROPS_FIELD)
      .build();

}
