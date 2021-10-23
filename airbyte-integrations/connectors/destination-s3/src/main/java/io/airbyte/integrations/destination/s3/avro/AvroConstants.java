/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import javax.security.auth.callback.NameCallback;
import tech.allegro.schema.json2avro.converter.JsonAvroConverter;

public class AvroConstants {

  // Field name with special character
  public static final String DOC_KEY_VALUE_DELIMITER = ":";
  public static final String DOC_KEY_ORIGINAL_NAME = "_airbyte_original_name";
  // This name must match ab_additional_col in source_s3/source_files_abstract/stream.py
  public static final String ADDITIONAL_PROPERTIES_FIELD_NAME = "_ab_additional_properties";
  public static final AvroNameTransformer NAME_TRANSFORMER = new AvroNameTransformer();
  public static final JsonAvroConverter JSON_CONVERTER = JsonAvroConverter.builder()
      .setNameTransformer(NAME_TRANSFORMER::getIdentifier)
      .setAdditionalPropertiesFieldName(ADDITIONAL_PROPERTIES_FIELD_NAME)
      .build();

}
