/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.util.Stringify;
import io.airbyte.integrations.destination.s3.util.NumericType;

public interface MetastoreFormatConfig extends S3FormatConfig {

  String getInputFormat();

  String getOutputFormat();

  String getSerializationLibrary();

  Stringify getStringifyType();

  // TODO (quazi-h) Is this the correct place to put these methods?
  //  This requires me to add overrides in MetastoreJsonlFormatConfig
  NumericType getNumericType();

  NumericType getDecimalScale();

}
